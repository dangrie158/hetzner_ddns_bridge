import json
from ipaddress import IPv4Address, IPv6Address
from typing import Literal, NamedTuple, NewType

ZoneId = NewType("ZoneId", str)
RecordId = NewType("RecordId", str)
ZoneName = NewType("ZoneName", str)
AuthKey = NewType("AuthKey", str)
RecordType = Literal[
    "A" "AAAA" "NS" "MX" "CNAME" "RP" "TXT" "SOA" "HINFO" "SRV" "DANE" "TLSA" "DS" "CAA"
]
IpAddress = IPv4Address | IPv6Address


class Record(NamedTuple):
    id: RecordId
    zone_id: ZoneId
    type: RecordType
    name: str
    value: str
    ttl: int = 60
    created: str = ""
    modified: str = ""

    def to_json(self) -> str:
        object_attributes = {
            "zone_id": f"{self.zone_id:s}",
            "type": f"{self.type:s}",
            "name": f"{self.name:s}",
            "value": f"{self.value:s}",
            "ttl": self.ttl,
        }
        if self.id is not None:
            object_attributes |= {
                "id": f"{self.id:s}",
            }

        return json.dumps(object_attributes)


class Error(NamedTuple):
    message: str


class Domain(NamedTuple):
    fqdn: str

    @property
    def parts(self) -> list[str]:
        return self.fqdn.split(".")

    @property
    def subdomain(self):
        return ".".join(self.parts[:-2])

    @property
    def zone(self):
        return ".".join(self.parts[-2:])

    def matches(self, other: str) -> bool:
        if other == "@" and self.fqdn == self.zone:
            return True
        if other == "*":
            return True
        if self.subdomain == other:
            return True

        return False
