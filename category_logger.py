import json
from pathlib import Path

def load_categories():
    """Load categories from the JSON file."""
    try:
        with open('categorias_taekwondo.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo categorias_taekwondo.json")
        return None

def generate_category_combinations(categories):
    """Generate all possible category combinations."""
    all_combinations = []
    
    for division, data in categories.items():
        niveles = data['NIVEL']
        
        # Handle divisions with different weight structures
        if isinstance(data['SEXO'], dict):
            # For divisions like CADETE, JUVENIL, MAYORES where weights differ by gender
            for nivel in niveles:
                for genero, pesos in data['SEXO'].items():
                    for peso in pesos:
                        categoria = f"{nivel} {division.replace('_', ' ')} {genero} {peso}"
                        all_combinations.append(categoria)
        else:
            # For divisions like PRE_INFANTIL, INFANTIL_A, etc.
            for nivel in niveles:
                for genero in data['SEXO']:
                    for peso in data['PESOS']:
                        categoria = f"{nivel} {division.replace('_', ' ')} {genero} {peso}"
                        all_combinations.append(categoria)
    
    return sorted(all_combinations)

def display_categories(combinations):
    """Display categories in a formatted way."""
    print("\n=== TODAS LAS CATEGORÍAS POSIBLES ===\n")
    
    current_nivel = None
    current_division = None
    
    for categoria in combinations:
        parts = categoria.split()
        nivel = parts[0]
        division = ' '.join(parts[1:3]) if parts[1] == "PRE" else parts[1]
        
        # Print headers for better organization
        if nivel != current_nivel:
            print(f"\n[{nivel}]")
            current_nivel = nivel
            current_division = None
        
        if division != current_division:
            print(f"\n  {division}:")
            current_division = division
        
        print(f"    • {categoria}")

def main():
    """Main function to run the category logger."""
    print("\n🔍 Cargando categorías de taekwondo...")
    
    # Load categories from JSON
    categories = load_categories()
    if not categories:
        return
    
    # Generate all possible combinations
    combinations = generate_category_combinations(categories)
    
    # Display the categories
    display_categories(combinations)
    
    print(f"\n✅ Total de categorías posibles: {len(combinations)}")

if __name__ == "__main__":
    main() 