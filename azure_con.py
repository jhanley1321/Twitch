# check_adls_interactive.py
from azure.identity import InteractiveBrowserCredential
from azure.storage.filedatalake import DataLakeServiceClient

ACCOUNT_NAME = "<streamalyticsdatalake>"        # e.g., streamalyticsdatalake
FILESYSTEM = "twitch-vod-chat"                      # your container name

def main():
    print("Opening browser to sign in...")
    cred = InteractiveBrowserCredential()  # forces a browser login prompt
    svc  = DataLakeServiceClient(f"https://{ACCOUNT_NAME}.dfs.core.windows.net", credential=cred)

    print("Listing file systems (containers):")
    for fs in svc.list_file_systems():
        print(" -", fs.name)

    fs = svc.get_file_system_client(FILESYSTEM)
    props = fs.get_file_system_properties()
    print(f"\nConnected to filesystem: {FILESYSTEM}")
    print("ETag:", props['etag'])

    print("\nTop-level paths:")
    for p in fs.get_paths(path="", recursive=False):
        print(" -", ("dir" if p.is_directory else "file"), p.name)

if __name__ == "__main__":
    main()