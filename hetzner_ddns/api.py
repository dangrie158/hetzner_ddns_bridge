from typing import Mapping

import requests

from hetzner_ddns.models import (
    AuthKey,
    Domain,
    Error,
    Record,
    RecordId,
    RecordType,
    ZoneId,
    ZoneName,
)

IP_VERSION_TO_RECORD_TYPE = {4: "A", 6: "AAAA"}


class ApiClient:
    def __init__(self, auth_key: AuthKey) -> None:
        self.auth_key = auth_key

    def get_all_zones(self) -> Mapping[ZoneName, ZoneId]:
        response = requests.get(
            url="https://dns.hetzner.com/api/v1/zones",
            headers={
                "Auth-API-Token": self.auth_key,
            },
        ).json()

        return {entry["name"]: entry["id"] for entry in response["zones"]}

    def get_zone_id(self, domain: Domain) -> ZoneId | None:
        all_zones = self.get_all_zones()
        for zone_name, zone_id in all_zones.items():
            if domain.zone == zone_name:
                return zone_id
        return None

    def get_all_zone_records(self, zone_id: ZoneId) -> list[Record]:
        response = requests.get(
            url="https://dns.hetzner.com/api/v1/records",
            params={
                "zone_id": zone_id,
            },
            headers={
                "Auth-API-Token": self.auth_key,
            },
        ).json()

        return [Record(**record_data) for record_data in response["records"]]

    def find_record_id_for_domain(
        self, records: list[Record], domain: Domain, record_type: RecordType
    ) -> RecordId | None:
        matching_records: list[Record] = []
        for record in records:
            if domain.matches(record.name) and record.type == record_type:
                matching_records.append(record)

        if len(matching_records) > 1:
            raise KeyError(f"Found multiple entries for {domain!r}")

        return matching_records[0].id if len(matching_records) == 1 else None

    def create_record(self, record: Record) -> Record | Error:
        response = requests.post(
            url="https://dns.hetzner.com/api/v1/records",
            headers={
                "Content-Type": "application/json",
                "Auth-API-Token": self.auth_key,
            },
            data=record.to_json(),
        ).json()

        if "error" in response:
            if "message" in response["error"]:
                return Error(response["error"]["message"])
            return Error(response["error"])

        return Record(**response["record"])

    def update_record(self, record: Record) -> Record | Error:
        response = requests.put(
            url=f"https://dns.hetzner.com/api/v1/records/{record.id}",
            headers={
                "Content-Type": "application/json",
                "Auth-API-Token": self.auth_key,
            },
            data=record.to_json(),
        ).json()

        if "error" in response:
            if "message" in response["error"]:
                return Error(response["error"]["message"])
            return Error(response["error"])

        return Record(**response["record"])
