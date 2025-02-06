from dataclasses import dataclass


@dataclass
class AgencyIndex:
    headline: str


index_context = {
    "cst": AgencyIndex(headline="Get a reduced fare on CST public transportation when you tap to ride"),
    "mst": AgencyIndex(headline="Get a reduced fare on MST public transportation when you tap to ride"),
    "nevco": AgencyIndex(headline="Get a reduced fare on Nevada County Connects public transportation when you tap to ride"),
    "sacrt": AgencyIndex(headline="Get a reduced fare on SacRT buses when you tap to ride"),
    "sbmtd": AgencyIndex(headline="Get a reduced fare on Santa Barbara MTD buses when you tap to ride"),
}
