from django.db import migrations
from django.utils.translation import gettext_lazy as _


def load_initial_data(app, *args, **kwargs):
    PemData = app.get_model("core", "PemData")

    PemData.objects.create(
        text="""
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyYo6Pe9OSfPGX0oQXyLA
blOwrMgc/j1JlF07b1ahq1lc3FH0XEk3Dzqbt9NuQs8hz6493vBNtNWTpVmvbGe4
VX3UjhpEARhN3m4jf/Z2OEuDt2A9q19NLSjgeyhieLkYLwN1ezYXrkn7cfOngcJM
nGDXp45CaA+g3DzasrjETnKUdqecCzJ3FJ/RRwfibrju7eS/8s6H03nvydzeAJzT
kEv7Fic2JJEUhh2rJhyLxt+qKkIYeBG+5fBri4miaS8FPnD/yjZzEAFsQc7n0dGq
DAhSJS8tYNmXFmGlaCfRUBNV3mvOx0vFPuH21WQ5KKZxZP0e64/uQdotbPIImiyR
JwIDAQAB
-----END PUBLIC KEY-----

""",
        label="Eligibility server public key",
    )

    PemData.objects.create(
        text="""
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1pt0ZoOuPEVPJJS+5r884zcjZLkZZ2GcPwr79XOLDbOi46on
Ca79kjRnhS0VUK96SwUPS0z9J5mDA5LSNL2RoxFb5QGaevnJY828NupzTNdUd0sY
JK3kRjKUggHWuB55hwJcH/Dx7I3DNH4NL68UAlK+VjwJkfYPrhq/bl5z8ZiurvBa
5C1mDxhFpcTZlCfxQoas7D1d+uPACF6mEMbQNd3RaIaSREO50NvNywXIIt/OmCiR
qI7JtOcn4eyh1I4j9WtlbMhRJLfwPMAgY5epTsWcURmhVofF2wVoFbib3JGCfA7t
z/gmP5YoEKnf/cumKmF3e9LrZb8zwm7bTHUViwIDAQABAoIBAQCIv0XMjNvZS9DC
XoXGQtVpcxj6dXfaiDgnc7hZDubsNCr3JtT5NqgdIYdVNQUABNDIPNEiCkzFjuwM
uuF2+dRzM/x6UCs/cSsCjXYBCCOwMwV/fjpEJQnwMQqwTLulVsXZYYeSUtXVBf/8
0tVULRty34apLFhsyX30UtboXQdESfpmm5ZsqsZJlYljw+M7JxRMneQclI19y/ya
hPWlfhLB9OffVEJXGaWx1NSYnKoCMKqE/+4krROr6V62xXaNyX6WtU6XiT7C6R5A
PBxfhmoeFdVCF6a+Qq0v2fKThYoZnV4sn2q2An9YPfynFYnlgzdfnAFSejsqxQd0
fxYLOtMBAoGBAP1jxjHDJngZ1N+ymw9MIpRgr3HeuMP5phiSTbY2tu9lPzQd+TMX
fhr1bQh2Fd/vU0u7X0yPnTWtUrLlCdGnWPpXivx95GNGgUUIk2HStFdrRx+f2Qvk
G8vtLgmSbjQ26UiHzxi9Wa0a41PWIA3TixkcFrS2X29Qc4yd6pVHmicfAoGBANjR
Z8aaDkSKLkq5Nk1T7I0E1+mtPoH1tPV/FJClXjJrvfDuYHBeOyUpipZddnZuPGWA
IW2tFIsMgJQtgpvgs52NFI7pQGJRUPK/fTG+Ycocxo78TkLr/RIj8Kj5brXsbZ9P
3/WBX5GAISTSp1ab8xVgK/Tm07hGupKVqnY2lCAVAoGAIql0YjhE2ecGtLcU+Qm8
LTnwpg4GjmBnNTNGSCfB7IuYEsQK489R49Qw3xhwM5rkdRajmbCHm+Eiz+/+4NwY
kt5I1/NMu7vYUR40MwyEuPSm3Q+bvEGu/71pL8wFIUVlshNJ5CN60fA8qqo+5kVK
4Ntzy7Kq6WpC9Dhh75vE3ZcCgYEAty99uXtxsJD6+aEwcvcENkUwUztPQ6ggAwci
je9Z/cmwCj6s9mN3HzfQ4qgGrZsHpk4ycCK655xhilBFOIQJ3YRUKUaDYk4H0YDe
Osf6gTP8wtQDH2GZSNlavLk5w7UFDYQD2b47y4fw+NaOEYvjPl0p5lmb6ebAPZb8
FbKZRd0CgYBC1HTbA+zMEqDdY4MWJJLC6jZsjdxOGhzjrCtWcIWEGMDF7oDDEoix
W3j2hwm4C6vaNkH9XX1dr5+q6gq8vJQdbYoExl22BGMiNbfI3+sLRk0zBYL//W6c
tSREgR4EjosqQfbkceLJ2JT1wuNjInI0eR9H3cRugvlDTeWtbdJ5qA==
-----END RSA PRIVATE KEY-----
""",
        label="Benefits client private key",
    )

    PemData.objects.create(
        text="""
-----BEGIN CERTIFICATE-----
PEM DATA
-----END CERTIFICATE-----
""",
        label="Dummy certificate",
    )

    AuthProvider = app.get_model("core", "AuthProvider")

    AuthProvider.objects.create(
        sign_in_button_label=_("eligibility.buttons.signin"),
        sign_out_button_label=_("eligibility.buttons.signout"),
        client_name="benefits-oauth-client-name",
        client_id="benefits-oauth-client-id",
        authority="https://example.com",
        scope="verify:type1",
        claim="type1",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]
