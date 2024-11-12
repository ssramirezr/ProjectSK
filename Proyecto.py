from collections import defaultdict
from rich import print
from rich.table import Table

# Función para calcular el conjunto First de todos los símbolos no terminales
def compute_first(grammar, non_terminals):
    first = defaultdict(set)
    
    # Función recursiva para encontrar First de un símbolo
    def find_first(symbol):
        # Si es un terminal ε, su First es el propio símbolo
        if symbol not in non_terminals or symbol == 'e':
            return {symbol}
        
        # Si es un no terminal, calcula su First
        if symbol not in first:
            first[symbol] = set()
            for production in grammar[symbol]:
                first_symbol = production[0]
                
                # Si el primer símbolo es un terminal, solo agrega su primer carácter
                if first_symbol.islower():
                    first[symbol].add(first_symbol[0])
                    continue
                
                # Si el primer símbolo es un no terminal, calcular su First
                first[symbol].update(find_first(first_symbol))
                
                # Si 'e' está en el First del primer símbolo, considera el resto de la producción
                if 'e' in first[first_symbol]:
                    for prod_symbol in production[1:]:
                        next_first = find_first(prod_symbol) - {'e'}
                        first[symbol].update(next_first)
                        if 'e' not in find_first(prod_symbol):
                            break
                    else:
                        first[symbol].add('e')  # Si todos pueden derivar en ε

        return first[symbol]
    
    # Calcular First para todos los no terminales
    for non_terminal in non_terminals:
        find_first(non_terminal)
    
    return first

# Función para calcular el conjunto Follow de todos los símbolos no terminales
def compute_follow(grammar, non_terminals, first):
    follow = defaultdict(set)
    start_symbol = non_terminals[0]
    follow[start_symbol].add('$')

    # Función recursiva para calcular Follow
    def find_follow(symbol):
        for lhs in grammar:
            for production in grammar[lhs]:
                if symbol in production:
                    idx = production.index(symbol)
                    
                    # Caso 2: Añadir first del siguiente símbolo a follow del símbolo actual
                    while idx < len(production) - 1:
                        idx += 1
                        next_symbol = production[idx]
                        
                        if next_symbol not in non_terminals:
                            follow[symbol].add(next_symbol)
                            break
                        else:
                            next_first = first[next_symbol] - {'e'}
                            follow[symbol].update(next_first)
                            
                            # Si el siguiente símbolo no puede derivar en ε, se detiene
                            if 'e' not in first[next_symbol]:
                                break
                    else:
                        # Caso 3: Si es el último en la producción, heredar follow del símbolo izquierdo
                        if lhs != symbol:
                            follow[symbol].update(find_follow(lhs))

        return follow[symbol]

    # Calcular follow para cada no terminal
    for non_terminal in non_terminals:
        find_follow(non_terminal)

    return follow

# Función para verificar si la gramática es LL(1)
def is_ll1(grammar, non_terminals, first, follow):
    for non_terminal in non_terminals:
        productions = grammar[non_terminal]
        first_sets = []
        
        # Obtener el conjunto First de cada producción
        for production in productions:
            first_of_production = set()
            for symbol in production:
                first_of_production |= first[symbol]
                if 'e' not in first[symbol]:
                    break
            else:
                # Si toda la producción puede ser vacía, añadir Follow(no_terminal)
                first_of_production |= follow[non_terminal]
            
            # Comprobar que no haya intersección con otros conjuntos First de producciones de este no terminal
            for other_set in first_sets:
                if first_of_production & other_set:
                    return False  # Si hay intersección, no es LL(1)
            first_sets.append(first_of_production)
    
    return True

# función para calcular el conjunto First de una cadena
def compute_first_of_string(string, first):
    result_first = set()
    for symbol in string:
        # Si el símbolo es un terminal, añádelo directamente al conjunto First de la cadena
        if symbol.islower():
            result_first.add(symbol)
            break
        # Si es un no terminal, añade su conjunto First
        result_first |= first[symbol] - {'e'}
        if 'e' not in first[symbol]:
            break
    else:
        # Si todos los símbolos pueden derivar en vacío, incluye 'e' en el resultado
        result_first.add('e')
    return result_first

# Función para construir la tabla de análisis predictivo (parsing table)
def construct_parsing_table(grammar, non_terminals, first, follow):
    table = defaultdict(dict)
    for non_terminal in non_terminals:
        for production in grammar[non_terminal]:
            # Calcular First de la producción
            production_first = compute_first_of_string(production, first)
            production_str = " ".join(production)  # Convertir la producción a cadena
            for terminal in production_first - {'e'}:
                table[non_terminal][terminal] = production_str
            # Si 'e' está en First(production), añadir producción para cada símbolo en Follow(no_terminal)
            if 'e' in production_first:
                for terminal in follow[non_terminal]:
                    table[non_terminal][terminal] = production_str
    return table

# Función para mostrar la tabla de análisis predictivo
def display_parsing_table(table, terminals, non_terminals):
    parse_table = Table(title="Parsing Table", show_header=True, header_style="bold magenta")
    parse_table.add_column("Non-Terminal")
    for terminal in sorted(terminals | {'$'}):
        parse_table.add_column(terminal)

    for non_terminal in sorted(non_terminals):
        row = [non_terminal]
        for terminal in sorted(terminals | {'$'}):
            entry = table[non_terminal].get(terminal, "")
            row.append(entry)
        parse_table.add_row(*row)
    print(parse_table)

# Función principal que procesa la entrada y realiza los cálculos de First y Follow
def process_grammar_cases():
    n = int(input())  # Número de casos
    cases = []

    for _ in range(n):
        m = int(input())  # Número de no terminales
        grammar = defaultdict(list)
        non_terminals = []
        terminals = set()

        for _ in range(m):
            line = input().strip().split()
            non_terminal = line[0]
            if non_terminal not in non_terminals:
                non_terminals.append(non_terminal)
            derivations = line[1:]
            processed_derivations = []

            # Procesar cada derivación correctamente
            for production in derivations:
                current_symbol = ""
                parsed_production = []
                for i, char in enumerate(production):
                    if char.isupper():  # Detecta un no terminal
                        if current_symbol:  # Añadir terminal acumulado antes del no terminal
                            parsed_production.append(current_symbol)
                            terminals.add(current_symbol)
                            current_symbol = ""
                        parsed_production.append(char)
                    elif char == ' ':
                        if current_symbol:  # Añadir el terminal acumulado
                            parsed_production.append(current_symbol)
                            terminals.add(current_symbol)
                            current_symbol = ""
                    else:
                        current_symbol += char
                        if i == len(production) - 1:  # Último carácter de la producción
                            parsed_production.append(current_symbol)
                            terminals.add(current_symbol)
                            current_symbol = ""
                
                processed_derivations.append(parsed_production)
            
            grammar[non_terminal].extend(processed_derivations)
        
        # Almacenar los casos para procesarlos después
        cases.append((grammar, non_terminals, terminals))

    # Procesar cada caso después de haber ingresado todos los datos
    for grammar, non_terminals, terminals in cases:
        # Calcular First y Follow
        first = compute_first(grammar, non_terminals)
        follow = compute_follow(grammar, non_terminals, first)

        # Imprimir conjuntos First en el mismo orden de aparición
        for non_terminal in non_terminals:
            print(f"First({non_terminal}) = {{ {', '.join(sorted(first[non_terminal]))} }}")

        # Imprimir conjuntos Follow en el mismo orden de aparición
        for non_terminal in non_terminals:
            print(f"Follow({non_terminal}) = {{ {', '.join(sorted(follow[non_terminal]))} }}")
        
        print()  # Línea en blanco entre los casos

        # Verificar si la gramática es LL(1)
        # if is_ll1(grammar, non_terminals, first, follow):
        #     print("[bold green]La gramática es LL(1)[/bold green]")
            # string = input("Ingresa la cadena para calcular su conjunto First: ").strip()
            # string_first = compute_first_of_string(string, first)
            # print(f"First({string}) = {{ {', '.join(sorted(string_first))} }}")

        # Construir y mostrar la tabla de análisis predictivo
            # parsing_table = construct_parsing_table(grammar, non_terminals, first, follow)
            # display_parsing_table(parsing_table, terminals, non_terminals)

        # else:
        #     print("[bold red]La gramática no es LL(1)[/bold red]")

# Ejecutar el programa
if __name__ == "__main__":
    process_grammar_cases()
