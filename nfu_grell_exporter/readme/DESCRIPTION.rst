This module adds a CSV exporter action to Sale Order Batch module.
It exports the article number (default_code) and the qty of the Sale Order Batch
Product view.

Grell bietet die Möglichkeit Bestellungen als CSV hochzuladen. Dafür werden lediglich 2 Spalten benötigt
\|Artnr\|Menge\|

* Artnr
    Artikelnummer beim Hersteller also Grell
    Das ist aktuell der default_code, falls wir den mal prefixen, muss das hier angepasst werden oder wir gehen auf Das Lieferantenmodel
* Menge
    Bestellmenge/Gebindegröße