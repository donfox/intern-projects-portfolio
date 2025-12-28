#!/bin/bash

show_main_menu() {
  echo ""
  echo "Provider Vault Demo Menu"
  echo "======================="
  echo ""
  echo "1. Start Web App (Phoenix + AI Service)"
  echo "2. Run Elixir CLI (Phase 1 prototype)"
  echo "3. Run Python AI Interactive Demo"
  echo "4. Exit"
  echo ""
  read -p "Choose an option (1-4): " choice

  case $choice in
    1)
      echo "Starting web app..."
      ./start.sh
      ;;
    2)
      show_cli_menu
      ;;
    3)
      echo "Starting Python AI Interactive Demo..."
      cd apps/ai_service
      source .venv/bin/activate
      python interactive_demo.py
      cd ../..
      show_main_menu
      ;;
    4)
      echo "Goodbye!"
      exit 0
      ;;
    *)
      echo "Invalid option"
      show_main_menu
      ;;
  esac
}

show_cli_menu() {
  echo ""
  echo "Elixir CLI Commands:"
  echo "===================="
  echo "1. Fetch providers from sources"
  echo "2. List all providers (limit 20)"
  echo "3. Show database statistics"
  echo "4. Search providers"
  echo "5. Back to main menu"
  echo ""
  read -p "Choose (1-5): " cli_choice
  
  case $cli_choice in
    1) 
      prototypes/cli_v1_7/provider_vault_cli fetch
      ;;
    2) 
      prototypes/cli_v1_7/provider_vault_cli list --limit 20
      ;;
    3) 
      prototypes/cli_v1_7/provider_vault_cli stats
      ;;
    4) 
      read -p "Enter search term: " search_term
      prototypes/cli_v1_7/provider_vault_cli search "$search_term"
      ;;
    5) 
      show_main_menu
      return
      ;;
    *) 
      echo "Invalid option"
      ;;
  esac
  
  echo ""
  read -p "Press Enter to continue..."
  show_cli_menu
}

# Start the menu
show_main_menu
