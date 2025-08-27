import os
import pickle
import time
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Use this scope for full Gmail access
SCOPES = ['https://mail.google.com/']


def get_gmail_service():
    """Authenticate and create a Gmail service instance."""
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def search_emails_in_batches(service, query, max_results=None):
    """Search for emails in batches with pagination."""
    messages = []
    page_token = None
    batch_size = 500  # Maximum allowed by Gmail API

    try:
        while True:
            # Calculate how many more results we need
            remaining = max_results - len(messages) if max_results else batch_size
            current_batch_size = min(batch_size, remaining) if max_results else batch_size

            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=current_batch_size,
                pageToken=page_token
            ).execute()

            batch_messages = results.get('messages', [])
            messages.extend(batch_messages)

            # Check if we've reached the limit or end of results
            page_token = results.get('nextPageToken')

            if (max_results and len(messages) >= max_results) or not page_token:
                break

            # Add a small delay to avoid rate limiting
            time.sleep(0.1)

    except HttpError as error:
        print(f'An error occurred during search: {error}')

    return messages[:max_results] if max_results else messages


def delete_emails_in_batches(service, messages, batch_size=500):
    """Delete emails in batches to handle large volumes."""
    if not messages:
        print("No messages to delete.")
        return 0

    total_deleted = 0
    batch_size = min(batch_size, 500)  # Gmail API limit is 500 per batch

    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]

        try:
            # Batch delete messages
            message_ids = [msg['id'] for msg in batch]
            service.users().messages().batchDelete(
                userId='me',
                body={'ids': message_ids}
            ).execute()

            total_deleted += len(batch)
            print(f"Deleted batch {i // batch_size + 1}: {len(batch)} emails (Total: {total_deleted})")

            # Add delay to avoid rate limiting (Gmail API quotas)
            time.sleep(1)

        except HttpError as error:
            print(f'Error deleting batch {i // batch_size + 1}: {error}')
            # Continue with next batch instead of stopping completely
            continue

    return total_deleted


def estimate_email_count(service, query):
    """Estimate the total number of emails matching the query."""
    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=1
        ).execute()

        return results.get('resultSizeEstimate', 0)
    except HttpError as error:
        print(f'Error estimating email count: {error}')
        return 0


def main():
    # Authenticate and create Gmail service
    print("Logging into Gmail...")
    service = get_gmail_service()
    print("Successfully logged in!")

    while True:
        # Get search query from user
        sender = input(
            "\nWhich emails would you like to remove? (Enter sender name or email, or 'quit' to exit): ").strip()

        if sender.lower() == 'quit':
            break

        if not sender:
            print("Please enter a valid sender name or email.")
            continue

        # Build search query
        query = f"from:{sender}"

        # Estimate total emails first
        print(f"Estimating total emails from '{sender}'...")
        total_estimate = estimate_email_count(service, query)

        if total_estimate == 0:
            print(f"No emails found from '{sender}'.")
            continue

        print(f"Estimated {total_estimate} emails from '{sender}'")

        # Ask if user wants to set a limit
        set_limit = input("Would you like to set a limit on the number of emails to delete? (yes/no): ").strip().lower()

        max_results = None
        if set_limit == 'yes':
            try:
                max_results = int(input("Enter the maximum number of emails to delete: "))
                if max_results <= 0:
                    print("Please enter a positive number.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue

        # Confirm deletion
        target_count = max_results if max_results else total_estimate
        confirm = input(f"About to delete up to {target_count} emails. Are you sure? (yes/no): ").strip().lower()

        if confirm != 'yes':
            print("Deletion cancelled.")
            continue

        # Search for emails in batches
        print(f"Searching for emails from '{sender}'...")
        messages = search_emails_in_batches(service, query, max_results)

        if not messages:
            print(f"No emails found from '{sender}'.")
            continue

        print(f"Found {len(messages)} emails ready for deletion.")

        # Final confirmation
        final_confirm = input(f"Ready to delete {len(messages)} emails. Proceed? (yes/no): ").strip().lower()

        if final_confirm != 'yes':
            print("Deletion cancelled.")
            continue

        # Delete emails in batches
        print(f"Starting deletion of {len(messages)} emails...")
        print("This may take several minutes for large volumes...")

        start_time = time.time()
        deleted_count = delete_emails_in_batches(service, messages)
        end_time = time.time()

        elapsed_time = end_time - start_time
        print(f"\nSuccessfully deleted {deleted_count} emails in {elapsed_time:.2f} seconds!")

        if deleted_count < len(messages):
            print(f"Note: {len(messages) - deleted_count} emails may not have been deleted due to errors.")


if __name__ == '__main__':
    print("Gmail Bulk Email Deleter - Enterprise Edition")
    print("=============================================")
    print("Designed to handle thousands of emails efficiently")
    print("")

    if not os.path.exists('credentials.json'):
        print("Error: 'credentials.json' file not found.")
        print("Please create Gmail API credentials first.")
    else:
        main()