from app import check_for_interruption, resume_from_interrupt, show_conversation_history, stream_graph_updates


def main():
    """Enhanced main function with better user experience."""
    print("🎉 Party Planning Assistant - Enhanced with Memory & Human-in-the-Loop!")
    print("=" * 70)
    print("Features:")
    print("• 💾 Remembers entire conversation history")
    print("• 🔧 Can search party invites and web information")
    print("• 🤝 Can request human assistance for complex decisions")
    print("• 📜 View conversation history with 'history'")
    print("• 🔄 Resume interrupted conversations")
    print("• 🆔 Use different thread IDs for separate conversations")
    print("\nCommands:")
    print("• 'quit', 'exit', 'q' - Stop the assistant")
    print("• 'history' - Show recent conversation")
    print("• 'thread:ID' - Switch to thread ID (e.g., 'thread:party1')")
    print("• 'resume:your response' - Resume after human assistance request")
    print("=" * 70)
    
    current_thread = "1"
    
    while True:
        try:
            user_input = input(f"\n👤 You (Thread {current_thread}): ").strip()
            
            # Handle special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 Thanks for using Party Planning Assistant! Goodbye!")
                break
            
            elif user_input.lower() == "history":
                show_conversation_history(current_thread)
                continue
            
            elif user_input.lower().startswith("thread:"):
                new_thread = user_input[7:].strip()
                if new_thread:
                    current_thread = new_thread
                    print(f"\n🔄 Switched to thread: {current_thread}")
                else:
                    print("\n❌ Please provide a thread ID (e.g., 'thread:party1')")
                continue
            
            elif user_input.lower().startswith("resume:"):
                response_data = user_input[7:].strip()
                if response_data and check_for_interruption(current_thread):
                    resume_from_interrupt(response_data, current_thread)
                elif not response_data:
                    print("\n❌ Please provide your response (e.g., 'resume:I think we should invite John')")
                else:
                    print("\n💡 No interruption detected. Please continue with normal conversation.")
                continue
            
            elif not user_input:
                print("\n💡 Please enter a message or command.")
                continue
            
            # Check if we're in an interrupted state
            if check_for_interruption(current_thread):
                print(f"\n⏸️ This conversation is waiting for human input.")
                print(f"Use 'resume:your response' to continue, or start a new thread.")
                continue
            
            # Process normal user input
            stream_graph_updates(user_input, current_thread)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("💡 Try continuing the conversation or restart if issues persist.")


if __name__ == "__main__":
    main()
