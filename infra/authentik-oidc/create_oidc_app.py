#!/usr/bin/env python3
"""Reusable Authentik OIDC provider/app creator (run via `ak shell` inside CT147). Zero hardcoded secrets."""
import os, secrets
from authentik.providers.oauth2.models import OAuth2Provider, ScopeMapping, RedirectURI, RedirectURIMatchingMode
from authentik.core.models import Application
from authentik.flows.models import Flow
from authentik.crypto.models import CertificateKeyPair

NAME = os.environ["OIDC_APP_NAME"]
SLUG = os.environ["OIDC_APP_SLUG"]
CLIENT_ID = os.environ["OIDC_CLIENT_ID"]
REDIRECT_URI = os.environ["OIDC_REDIRECT_URI"]
LAUNCH_URL = os.environ["OIDC_LAUNCH_URL"]

auth_flow = Flow.objects.filter(designation="authorization").first()
inval_flow = Flow.objects.filter(designation="invalidation").first()
signing_key = CertificateKeyPair.objects.first()

prov = OAuth2Provider.objects.filter(client_id=CLIENT_ID).first()
if not prov:
    prov = OAuth2Provider.objects.create(
        name=f"{NAME} OIDC",
        authorization_flow=auth_flow,
        invalidation_flow=inval_flow,
        client_type="confidential",
        client_id=CLIENT_ID,
        client_secret=secrets.token_urlsafe(32),
        redirect_uris=[RedirectURI(RedirectURIMatchingMode.STRICT, REDIRECT_URI)],
        signing_key=signing_key,
    )
    prov.property_mappings.set(ScopeMapping.objects.filter(scope_name__in=["openid", "email", "profile"]))
    prov.save()

app, _ = Application.objects.get_or_create(slug=SLUG, defaults={"name": NAME, "provider": prov, "meta_launch_url": LAUNCH_URL})
if app.provider != prov:
    app.provider = prov
    app.save()
print(f"READY slug={SLUG} client_id={prov.client_id}")
