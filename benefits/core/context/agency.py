from django.db import models


class AgencySlug(models.TextChoices):
    # raw value, display value
    CST = "cst", "cst"
    MST = "mst", "mst"
    EDCTA = "edcta", "edcta"
    NEVCO = "nevco", "nevco"
    RABA = "raba", "raba"
    ROSEVILLE = "roseville", "roseville"
    SACRT = "sacrt", "sacrt"
    SBMTD = "sbmtd", "sbmtd"
    SLORTA = "slorta", "slorta"
    VCTC = "vctc", "vctc"
