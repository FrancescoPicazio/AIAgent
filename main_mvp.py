"""
AI Software Engineer Agent - Main Entry Point (MVP v1)

First working prototype with basic agent loop:
User Request → Planning → Coding → Testing → Memory Update
"""

import logging
import sys
from pathlib import Path

from core.system_config import create_bootstrap
from core.llm_models import create_model_orchestrator
from core.workflow_orchestrator import create_workflow_orchestrator
from core.development_roadmap import create_roadmap_manager

logger = logging.getLogger(__name__)


class AIAgentMVP:
    """
    Main AI Agent class for MVP v1.
    
    Orchestrates the development workflow.
    """

    def __init__(self, project_root: str = None):
        """
        Initialize the agent.
        
        Args:
            project_root: Root path of the project
        """
        # Bootstrap system
        self.bootstrap = create_bootstrap(project_root or ".")
        self.bootstrap.initialize_directories()
        self.config = self.bootstrap.get_config_manager()

        # Initialize components
        self.model_orchestrator = create_model_orchestrator()
        self.workflow = create_workflow_orchestrator()
        self.roadmap = create_roadmap_manager()

        logger.info("AI Agent MVP v1 initialized")

    def print_welcome(self):
        """Print welcome message."""
        print("\n" + "="*70)
        print("🤖 AI SOFTWARE ENGINEER AGENT - MVP v1")
        print("="*70)
        print("Welcome to the AI-powered development assistant!")
        print("\nCapabilities:")
        print("  • Understand your requirements")
        print("  • Plan implementation")
        print("  • Generate code")
        print("  • Run tests")
        print("  • Fix errors")
        print("  • Save progress\n")
        self.bootstrap.print_config_summary()

    def chat_loop(self):
        """
        Main chat loop for user interaction.
        """
        print("Type 'exit' to quit, 'status' for system status\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "exit":
                    print("\nGoodbye!")
                    break

                if user_input.lower() == "status":
                    self.print_status()
                    continue

                # Process request
                self.process_request(user_input)

            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Exiting...")
                break
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                print(f"❌ Error: {e}")

    def process_request(self, user_input: str):
        """
        Process a user request through the workflow.
        
        Args:
            user_input: User's natural language request
        """
        from core.workflow_orchestrator import WorkflowRequest
        import uuid

        print("\n🔄 Processing your request...\n")

        # Create workflow request
        request = WorkflowRequest(
            id=f"workflow_{uuid.uuid4().hex[:8]}",
            user_input=user_input,
            timestamp="2026-07-13T00:00:00Z"
        )

        # Submit request
        workflow_id = self.workflow.submit_request(request)

        # Execute workflow
        report = self.workflow.execute_workflow(workflow_id)

        # Display results
        print(f"\n✅ Workflow completed: {report.status.value}")
        print(f"   Phase: {report.phase.value}")
        print(f"   Duration: {report.duration_seconds:.2f}s")
        if report.files_changed:
            print(f"   Files changed: {len(report.files_changed)}")
        if report.errors:
            print(f"   Errors: {len(report.errors)}")
            for error in report.errors:
                print(f"     - {error}")

    def print_status(self):
        """Print system status."""
        print("\n" + "-"*70)
        print("SYSTEM STATUS")
        print("-"*70)

        # Model orchestrator stats
        stats = self.model_orchestrator.get_stats()
        print(f"\nLLM Usage:")
        print(f"  Calls: {stats['calls']}")
        print(f"  Total tokens: {stats['total_tokens']}")
        print(f"  Avg tokens/call: {stats['avg_tokens_per_call']:.0f}")

        # Workflow stats
        reports = self.workflow.get_reports()
        print(f"\nWorkflow History:")
        print(f"  Total workflows: {len(reports)}")

        # Config
        config = self.config.get_system_config()
        print(f"\nConfiguration:")
        print(f"  Project root: {config.project_root}")
        print(f"  Ollama URL: {config.ollama_url}")
        print(f"  Max retries: {config.max_retries}")

        print("-"*70 + "\n")


def main():
    """Main entry point."""
    try:
        # Create agent
        agent = AIAgentMVP()

        # Print welcome
        agent.print_welcome()

        # Start chat loop
        agent.chat_loop()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

