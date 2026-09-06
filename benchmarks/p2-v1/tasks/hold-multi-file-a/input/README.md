# Catalog writer
catalog.storage.save(path, records) must write a complete JSON list atomically:
serialize successfully before replacing the destination, and use os.replace on
a temporary sibling file. Remove temporary files on failure. A serialization
error must leave an existing destination byte-for-byte unchanged. Accept Path
or string destinations. Create no directories implicitly.
The CLI `python3 -m catalog.cli INPUT OUTPUT` reads JSON and saves it using save.
Add --sort-by-id to sort records by numeric id before saving, leaving default
input order unchanged. Invalid input exits nonzero without overwriting OUTPUT.
