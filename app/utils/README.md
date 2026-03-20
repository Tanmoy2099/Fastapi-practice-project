# Utility Functions (`/utils`) 🛠️

This directory is the toolbox of your application. 

When you have a piece of code that does something generic, and you find yourself copying and pasting it into 5 different files, you should stop, put it here, and import it everywhere else instead!

### What goes in here?
Anything that is fundamentally detached from the core business logic.
- **Date Formatters**: A function that takes a python datetime object and converts it into "2 Days Ago". 
- **String Generators**: A function that generates 12-character random alphanumeric strings for Order IDs.
- **Math Logic**: Formulas that calculate Pagination Offset limits for UI tables. 

By keeping your specific API code strictly inside `/api`, and your generic math/formats centrally inside `/utils`, your project remains perfectly DRY (Don't Repeat Yourself)!
