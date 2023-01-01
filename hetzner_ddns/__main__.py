import logging
from ipaddress import ip_address

from bottle import LocalRequest, abort, request, route, run

from hetzner_ddns.api import IP_VERSION_TO_RECORD_TYPE, ApiClient, Record
from hetzner_ddns.models import AuthKey, Domain, Error, IpAddress


def get_new_ips_from_request(request: LocalRequest) -> list[IpAddress]:
    new_ips: list[IpAddress] = []
    for param_name in ("ip4", "ip6"):
        if param_name in request.query:
            new_ips.append(ip_address(request.query[param_name]))
    return new_ips


@route("/update")
def update():
    try:
        domain = Domain(request.query["domain"])
        auth_key = AuthKey(request.query["auth_key"])
    except KeyError:
        abort(400, "You must pass 'domain' and 'auth_key' query parameters")

    api_client = ApiClient(auth_key)

    try:
        new_ips = get_new_ips_from_request(request)
    except ValueError as e:
        abort(400, f"You passed an invalid IP Address: {e}")
    if len(new_ips) == 0:
        abort(400, "You passed neither a new IPv4 nor a new IPv6 Address")

    zone_id = api_client.get_zone_id(domain)
    if zone_id is None:
        abort(400, f"Zone for domain '{domain}' not registered")

    records = api_client.get_all_zone_records(zone_id)
    for new_ip in new_ips:
        record_type = IP_VERSION_TO_RECORD_TYPE[new_ip.version]
        record_id = api_client.find_record_id_for_domain(records, domain, record_type)
        new_record = Record(record_id, zone_id, record_type, domain.subdomain, new_ip)
        if record_id is None:
            action = "create"
            response = api_client.create_record(new_record)
        else:
            action = "update"
            response = api_client.update_record(new_record)

        match response:
            case Record(id, zone_id, type, name, value, ttl):
                logger.info(f"{action}d entry: {name:<10} {type:>4} {ttl:>4}")
            case Error(message):
                logger.warning(f"Error while updating entry: {message}")
    return "OK"


if __name__ == "__main__":
    logger = logging.getLogger("hetzner_ddns")
    logger.setLevel(logging.INFO)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
    )
    run(host="0.0.0.0", port=80, debug=False)
