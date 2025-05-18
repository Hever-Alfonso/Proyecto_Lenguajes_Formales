# LL(1) and SLR(1) Grammar Parser

## Student Information
- **Full Names of Group Members:** Hever Andre Alfonso Jimenez and Moises Vergara Garces

## Environment Details
- **Operating System:** macOS Sequoia 15.4.1
- **Processor:** 2.4 GHz Intel Core i5 (quad-core)
- **Programming Language:** Python 3.13.0
- **Tools Used:** Standard Python libraries (no external dependencies)

## How to Run the Implementation

1. **Clone or Download the Repository:**
   - Use Git to clone this repository or download the ZIP file and extract it.

2. **Navigate to the Project Directory:**
   - Open a terminal and move into the project folder:
     ```bash
     cd Proyecto_Lenguajes_Formales
     ```

3. **Run the Program:**
   - Execute the parser using the following command:
     ```bash
     python3 project.py
     ```

   - The program expects the following input format:
     - First, an integer `n` indicating the number of nonterminals.
     - Then, `n` lines of productions in the format:
       ```
       <nonterminal> -> <production1> <production2> ...
       ```
     - Afterward, strings to test against the grammar (one per line).
     - An empty line ends the test input.

4. **Behavior:**
   - The program automatically determines whether the grammar is:
     - **LL(1) only**
     - **SLR(1) only**
     - **Both LL(1) and SLR(1)**
     - **Neither**
   - Depending on the result, it will allow you to test strings using the appropriate parser (LL(1) or SLR(1)).

## Additional Notes
- The program fully supports context-free grammars under the restrictions described in the project guidelines.
- Empty productions should be written as `e`.
- The program handles the construction of FIRST and FOLLOW sets, LL(1) and SLR(1) parsing tables, and simulates parsing via both techniques.
- No additional installations are required.