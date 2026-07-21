#!/usr/bin/env python3
import sys
import os
import traceback

def run_smoke_test():
    print("Running CI smoke test...")
    
    try:
        # Import core application modules
        import app.client
        import app.feature.credit_memo
        
        # Import monitoring sub-systems
        import monitoring.db.models
        import monitoring.tracing.async_writer
        import monitoring.tracing.decorators
        import monitoring.judge.scorer
        import monitoring.drift.scheduler_job
        import monitoring.regression.runner
        
        print("✅ All major modules imported successfully.")
        
    except Exception as e:
        print(f"❌ Smoke test failed! Import error: {e}")
        traceback.print_exc()
        sys.exit(1)
        
    print("Smoke test passed. System is ready for CI.")
    sys.exit(0)

if __name__ == "__main__":
    run_smoke_test()
