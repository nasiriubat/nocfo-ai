## How to Run

Python installation is required to run thia project, then:

```bash
python run.py
```

This will run the script and display a report showing which transactions matched with which attachments.

## How It Works

The matching happens in two steps:

### Step 1: Reference Number Matching
If a transaction and attachment have matching reference numbers, they're automatically linked as said in the task README file.
### Step 2: Multi-Factor Matching
When there's no referencw number, the algorithm checks three factors:
- Amount: Compares absolute values
- Date: Allows up to 30 days difference
- Counterparty: Uses name matching to handle name variations

If at least 2 out of 3 factors align then we can say its a match.

## Technical Decisions

- Helper functions handle normalization, date comparison, and name matching separately. I tried to add some comment before those function on what theu do.

- Both `find_attachment` and `find_transaction` use the same logic, just in reverse.
- The algorithm always produces the same results for the same inputs, which was priority in the task README file.

- The code efficiently handles missing data, different attachment types (invoices vs receipts), and various name formats.

I have only edited `src/match.py`.

Please feel free to ask for any confusing part. I will actively looking for email and reply asap.
