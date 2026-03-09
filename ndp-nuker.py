"""
ndp-nuker

Author: Andrej A <tunas@cryptolab.net>

Description:
    Bulk deletes phones from a Netsapiens manager portal.
    Designed to be run as a script, reading MAC addresses from stdin (one per line), ending input with a line starting with 'end'.

DISCLAIMER: This tool is for educational and administrative purposes only. Use responsibly and only on systems you have authorization to manage.
"""


import sys
import requests

# These cookies do not work and are provided for illustrative purposes.
# Please replace them with your own cookies, obtained from Chrome DevTools.
# You can obtain these cookies by pressing Ctrl+Shift+I, going to the Network Tab, and refreshing any Manager Portal page;
# then, clicking on the initial web request in that list and finding them in the "Request headers".

COOKIES = {
   "CAKEPHP": "f09234jkf09kss90fjkm0ca",
   "NetsapiensPortal_4562testdomain.com[locale]": "bmljZXRyeQ==.bm93YXk=",
   "NetsapiensPortal_4562testdomain.com[sub_domain]": "bmljZXRyeQ==.bm90Z29ubmFoYXBwZW4="
}

BASE_URL = "https://netsapiens-core/portal/inventory/delete/phones/"

def normalize_mac(mac):
    norm = ''.join(filter(str.isalnum, mac.strip())).upper()
    return norm

def get_macs_from_stdin():
    macs = set()
    for line in sys.stdin:
        if line.startswith('#'):
            continue
        if line.lower().startswith('end'):
            break
        norm = normalize_mac(line)
        if norm:
            macs.add(norm)
    return list(macs)

def main():
    macs = get_macs_from_stdin()
    if not macs:
        print("No MAC addresses found.")
        return
    print(f"MACs to delete ({len(macs)}):")
    for mac in macs:
        print(f"  {mac}")
    confirm = input("Proceed with deletion requests? Type 'yes' to continue: ").strip().lower()
    if confirm not in ("yes", "y"):
        print("Aborted.")
        return
    succeeded = 0
    failed = 0
    try:
        for mac in macs:
            url = BASE_URL + mac
            try:
                # !!! USER AGENT MUST MATCH THE USER AGENT WHERE THE CAKEPHP TOKEN WAS HARVESTED FROM. !!!
                print("Sending request to " + url)
                resp = requests.get(url, cookies=COOKIES, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"})
                resp.raise_for_status()
                print(f"Deletion request sent for {mac}: ({resp.status_code})")
                # Show where the response redirected to
                print(f"Redirected to: {resp.url}")
                if "has not been deleted" in resp.text:
                    print(f"Deletion failed for {mac}")
                    failed += 1
                    continue
                elif "been removed" in resp.text:
                    print(f"Deletion successful for {mac}")
                    succeeded += 1
            except Exception as e:
                print(f"Deletion request failed for {mac}: {e}")
                failed += 1
        print(f"\nDeletion requests complete. Succeeded: {succeeded}, Failed: {failed}")
    except KeyboardInterrupt:
        print(f"\nDeletion requests complete. Succeeded: {succeeded}, Failed: {failed}, Unknown: {len(macs) - succeeded - failed}")

if __name__ == "__main__":
    main()