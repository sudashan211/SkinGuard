"""
Toggle Demo Mode On/Off
Quick script to enable/disable real AI predictions
"""
import sys
from pathlib import Path

def toggle_demo_mode(enable_real_ai: bool):
    """Toggle demo mode in .env file"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Create it from .env.example first")
        return False
    
    # Read current .env
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update DEMO_MODE line
    updated = False
    new_lines = []
    target_value = "false" if enable_real_ai else "true"
    
    for line in lines:
        if line.startswith('DEMO_MODE='):
            new_lines.append(f'DEMO_MODE={target_value}\n')
            updated = True
        else:
            new_lines.append(line)
    
    # If DEMO_MODE not found, add it
    if not updated:
        new_lines.append(f'\nDEMO_MODE={target_value}\n')
    
    # Write back
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    return True

def main():
    print("=" * 60)
    print("SkinGuard Demo Mode Toggle")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        choice = sys.argv[1].lower()
    else:
        print("\nCurrent mode:")
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('DEMO_MODE='):
                        current = line.strip().split('=')[1]
                        if current.lower() == 'true':
                            print("  🔵 DEMO MODE (mock predictions)")
                        else:
                            print("  🟢 REAL AI MODE (actual predictions)")
                        break
        
        print("\nWhat would you like to do?")
        print("  1. Enable REAL AI (disable demo mode)")
        print("  2. Enable DEMO MODE (disable real AI)")
        print("  3. Cancel")
        
        choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ['1', 'real', 'ai']:
        print("\n🔄 Enabling REAL AI mode...")
        if toggle_demo_mode(enable_real_ai=True):
            print("✅ DEMO_MODE=false")
            print("\n📋 Next steps:")
            print("  1. Restart the backend server")
            print("  2. First request will take 30-60 seconds (model loading)")
            print("  3. Subsequent requests: 5-15 seconds each")
            print("\n⚠️  Use real skin lesion images, not portraits!")
        else:
            print("❌ Failed to update .env file")
    
    elif choice in ['2', 'demo', 'mock']:
        print("\n🔄 Enabling DEMO mode...")
        if toggle_demo_mode(enable_real_ai=False):
            print("✅ DEMO_MODE=true")
            print("\n📋 Next steps:")
            print("  1. Restart the backend server")
            print("  2. All requests will return mock data")
            print("  3. Instant responses (~0.5 seconds)")
        else:
            print("❌ Failed to update .env file")
    
    else:
        print("\n❌ Cancelled")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
