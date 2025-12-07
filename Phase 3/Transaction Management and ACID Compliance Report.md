# Lobster Notes - Transaction Management & ACID Compliance

**Date**: December 7, 2025

**Goal**: Adding ACID compliant transactions to existing sql files

---

## Objective
1. Add transactions to each procedure to ensure each remains independent
2. Outputs error messages when transaction fails
3. Adds ability to commit and rollback tranactions

---

## Implementation
Each procedure had a transaction added that returns an error message if something goes wrong and now declares an exit handler for the exception. 
This will call the rollback to return to the previous version preventing errors from being introduced into the database or crashing it. This adds Durability from the ACID principles since it only commits functional information and saves committed data.
Each transaction is also independent of each other and can only succeed or fail, meaning it is both Atomic and has Isolation.
These changes will ensure the data in our database remains more Consistent allowing it to pass all of the ACID principles.
