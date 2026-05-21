import base64
import xml.etree.ElementTree as ET

import requests

from odoo import _
from odoo.exceptions import UserError


PIM_VERSION = "v2_3_0"
SECURITY_BASE = "https://security.datanature.info"
PIM_BASE = "https://pim.datanature.info"


def get_datanature_bearer_token(self):
    """
    Obtain a bearer token from the DataNature API using the provided API key.
    """
    ICP = self.env["ir.config_parameter"].sudo()
    userid = ICP.get_param("data_nature_importer.data_nature_username")
    password = ICP.get_param("data_nature_importer.data_nature_key")
    token = None
    if userid and password:
        token_url = f"{SECURITY_BASE}/resources/security/accesstoken"
        payload = {"userid": userid, "password": password}
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        token_response = requests.post(
            token_url, json=payload, headers=headers, timeout=30
        )
        if token_response.status_code == 200:
            token_data = token_response.json()
            if token_data.get("status") == "SUCCESS":
                token = token_data.get("token")
                return token
        raise UserError(_("Failed to obtain DataNature bearer token"))
    raise UserError(_("No username and password configured for DataNature API"))


def _parse_products(xml_bytes):
    """
    Parse the <products> section from the DataNature XML and extract product information.
    """
    ns = {"dn": "http://pim.datanature.info"}
    root = ET.fromstring(xml_bytes)
    products = []
    for prod in root.findall(".//dn:product", ns):
        product_data = {
            "sys_id": prod.findtext("dn:sys_id", default="", namespaces=ns),
            "bio_id": prod.findtext("dn:sys_bio_id", default="", namespaces=ns),
            "version": prod.findtext("dn:sys_version_nr", default="", namespaces=ns),
            "gtin": prod.findtext("dn:idnr_gtin", default="", namespaces=ns),
            "name_short": prod.findtext(
                "dn:pbm_produktname_kurz", default="", namespaces=ns
            ),
            "name_medium": prod.findtext(
                "dn:pbm_produktname_mittel", default="", namespaces=ns
            ),
            "name_long": prod.findtext(
                "dn:pbm_produktname_lang", default="", namespaces=ns
            ),
            "bezeichnung": prod.findtext(
                "dn:pbm_bezeichnung_des_lebensmittels", default="", namespaces=ns
            ),
            "zutatenverzeichnis": prod.findtext(
                "dn:zut_zutatenverzeichnis", default="", namespaces=ns
            ),
            "zutatenlegende_txt": prod.findtext(
                "dn:zut_zutatenlegende_txt", default="", namespaces=ns
            ),
            "warengruppe_id": prod.findtext(
                "dn:pbm_warengruppe_id", default="", namespaces=ns
            ),
            "warengruppe_kuerzel": prod.findtext(
                "dn:pbm_warengruppe_kuerzel", default="", namespaces=ns
            ),
            "warengruppe_pfad": prod.findtext(
                "dn:pbm_warengruppe_pfad", default="", namespaces=ns
            ),
            "beschreibung_kurz": prod.findtext(
                "dn:markinf_produktbeschreibung_kurz", default="", namespaces=ns
            ),
            "beschreibung_mittel": prod.findtext(
                "dn:markinf_produktbeschreibung_mittel", default="", namespaces=ns
            ),
            "beschreibung_lang": prod.findtext(
                "dn:markinf_produktbeschreibung_lang", default="", namespaces=ns
            ),
            "images": [
                {
                    "id": img.findtext("dn:id", default="", namespaces=ns),
                    "name": img.findtext("dn:name", default="", namespaces=ns),
                    "mime_type": img.findtext(
                        "dn:mime_type", default="", namespaces=ns
                    ),
                    "default": img.findtext("dn:default", default="", namespaces=ns),
                    "size": img.findtext("dn:size", default="", namespaces=ns),
                    "img_width": img.findtext(
                        "dn:img_width", default="", namespaces=ns
                    ),
                    "img_height": img.findtext(
                        "dn:img_height", default="", namespaces=ns
                    ),
                    "last_modified": img.findtext(
                        "dn:last_modified", default="", namespaces=ns
                    ),
                }
                for img in prod.findall("dn:media_images/dn:dn:binary", ns)
                or prod.findall("dn:media_images/dn:binary", ns)
            ],
            "documents": [
                {
                    "id": doc.findtext("dn:id", default="", namespaces=ns),
                    "name": doc.findtext("dn:name", default="", namespaces=ns),
                    "mime_type": doc.findtext(
                        "dn:mime_type", default="", namespaces=ns
                    ),
                    "size": doc.findtext("dn:size", default="", namespaces=ns),
                    "last_modified": doc.findtext(
                        "dn:last_modified", default="", namespaces=ns
                    ),
                }
                for doc in prod.findall("dn:media_documents/dn:binary", ns)
            ],
        }
        products.append(product_data)
    return products


def get_datanature_metadata(self, gtin, token=None):
    """
    Fetch product metadata from DataNature API using the provided BNN and bearer token.
    """
    if not token:
        token = get_datanature_bearer_token(self)
        if not token:
            raise UserError(_("Failed to obtain DataNature bearer token"))
    url = f"{PIM_BASE}/resources/pim/if/{PIM_VERSION}/export/filter/idnr_gtin/{gtin}"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/xml"}
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        return _parse_products(response.content)
    raise UserError(_("Failed to fetch DataNature metadata"))


def _parse_brands(xml_bytes):
    """
    Parse the <brands> section from the DataNature XML and extract brand information.
    """
    ns = {"dn": "http://pim.datanature.info"}
    root = ET.fromstring(xml_bytes)
    brands = []
    for brand in root.findall(".//dn:brand", ns):
        brand_data = {
            "name": brand.findtext("dn:name", default="", namespaces=ns),
            "kuerzel": brand.findtext("dn:kuerzel", default="", namespaces=ns),
            "id": brand.findtext("dn:id", default="", namespaces=ns),
            "producer_id": brand.findtext("dn:producer_id", default="", namespaces=ns),
            "last_modified": brand.findtext(
                "dn:last_modified", default="", namespaces=ns
            ),
            "kernaussage_marke": brand.findtext(
                "dn:kernaussage_marke", default="", namespaces=ns
            ),
            "markenportrait": brand.findtext(
                "dn:markenportrait", default="", namespaces=ns
            ),
            "initiativen_engagement": brand.findtext(
                "dn:initiativen_engagement", default="", namespaces=ns
            ),
            "auszeichnungen": [
                {
                    "name": item.findtext("dn:name", default="", namespaces=ns),
                    "year": item.findtext("dn:year", default="", namespaces=ns),
                }
                for item in brand.findall(
                    "dn:auszeichnungen/dn:auszeichnungen_item", ns
                )
            ],
            "logo": {
                "id": brand.findtext("dn:logo/dn:id", default="", namespaces=ns),
                "name": brand.findtext("dn:logo/dn:name", default="", namespaces=ns),
                "size": brand.findtext("dn:logo/dn:size", default="", namespaces=ns),
                "mime_type": brand.findtext(
                    "dn:logo/dn:mime_type", default="", namespaces=ns
                ),
                "img_width": brand.findtext(
                    "dn:logo/dn:img_width", default="", namespaces=ns
                ),
                "img_height": brand.findtext(
                    "dn:logo/dn:img_height", default="", namespaces=ns
                ),
                "last_modified": brand.findtext(
                    "dn:logo/dn:last_modified", default="", namespaces=ns
                ),
            },
            "social_media": [
                {
                    "social_media_id": item.findtext(
                        "dn:social_media_id", default="", namespaces=ns
                    ),
                    "url": item.findtext("dn:url", default="", namespaces=ns),
                }
                for item in brand.findall("dn:social_media/dn:social_media_item", ns)
            ],
            "adr_invb_name": brand.findtext(
                "dn:adr_invb_name", default="", namespaces=ns
            ),
            "adr_invb_strasse": brand.findtext(
                "dn:adr_invb_strasse", default="", namespaces=ns
            ),
            "adr_invb_plz": brand.findtext(
                "dn:adr_invb_plz", default="", namespaces=ns
            ),
            "adr_invb_ort": brand.findtext(
                "dn:adr_invb_ort", default="", namespaces=ns
            ),
            "adr_invb_land_id": brand.findtext(
                "dn:adr_invb_land_id", default="", namespaces=ns
            ),
        }
        brands.append(brand_data)
    return brands


def get_datanature_image(self, image_id, token=None):
    """
    Fetch image binary data from DataNature API using the image ID and bearer token.
    Returns the image content (bytes).
    """
    if not token:
        token = get_datanature_bearer_token(self)
        if not token:
            raise UserError(_("Failed to obtain DataNature bearer token"))
    url = f"{PIM_BASE}/resources/pim/if/{PIM_VERSION}/export/binary/media_images/{image_id}"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/octet-stream"}
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        image = base64.b64encode(response.content).decode("ascii")
        return image
    raise UserError(_("Failed to fetch DataNature image for ID: %s") % image_id)
