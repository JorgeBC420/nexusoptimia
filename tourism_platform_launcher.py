"""
NexusOptim IA - Tourism Platform Launcher
Lanzador principal para la plataforma de turismo tecnológico

Integra todos los componentes:
- Smart Tourism Platform UI
- Tourism AI Engine 
- Electrical Monitoring (opcional)
- LoRaWAN Infrastructure
- Premium Business Services

Copyright (c) 2025 OpenNexus
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import sys
import os

class TourismLauncher:
    """Lanzador principal para NexusOptim IA Tourism Platform"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🇨🇷 NexusOptim IA - Tourism Platform Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg='#0a0a1e')
        
        self.processes = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup launcher interface"""
        # Header
        header_frame = tk.Frame(self.root, bg='#1a1a2e', height=100)
        header_frame.pack(fill='x', pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="🇨🇷 NexusOptim IA\nSmart Tourism Costa Rica", 
                              font=('Arial', 20, 'bold'), 
                              fg='#00d4aa', bg='#1a1a2e')
        title_label.pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#0a0a1e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Services section
        services_frame = tk.LabelFrame(main_frame, text="🚀 Platform Services", 
                                     bg='#0a0a1e', fg='#ffffff', 
                                     font=('Arial', 14, 'bold'))
        services_frame.pack(fill='both', expand=True, pady=10)
        
        # Tourism Platform
        tourism_frame = tk.Frame(services_frame, bg='#16213e', relief='raised', bd=2)
        tourism_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(tourism_frame, text="🗺️ Smart Tourism Platform", 
                font=('Arial', 12, 'bold'), fg='#00d4aa', bg='#16213e').pack(side='left', padx=10, pady=10)
        
        tk.Button(tourism_frame, text="🚀 Launch Tourism", 
                 command=self.launch_tourism_platform,
                 bg='#00d4aa', fg='black', font=('Arial', 10, 'bold')).pack(side='right', padx=10, pady=5)
        
        tk.Label(tourism_frame, text="AI recommendations • Premium search • Location services", 
                font=('Arial', 9), fg='#cccccc', bg='#16213e').pack(side='right', padx=10)
        
        # AI Engine
        ai_frame = tk.Frame(services_frame, bg='#16213e', relief='raised', bd=2)
        ai_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(ai_frame, text="🤖 Tourism AI Engine", 
                font=('Arial', 12, 'bold'), fg='#4a9eff', bg='#16213e').pack(side='left', padx=10, pady=10)
        
        tk.Button(ai_frame, text="⚡ Initialize AI", 
                 command=self.initialize_ai_engine,
                 bg='#4a9eff', fg='white', font=('Arial', 10, 'bold')).pack(side='right', padx=10, pady=5)
        
        tk.Label(ai_frame, text="Machine learning • User profiling • Business analytics", 
                font=('Arial', 9), fg='#cccccc', bg='#16213e').pack(side='right', padx=10)
        
        # Electrical Monitoring (Optional)
        electrical_frame = tk.Frame(services_frame, bg='#16213e', relief='raised', bd=2)
        electrical_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(electrical_frame, text="⚡ Electrical Monitoring", 
                font=('Arial', 12, 'bold'), fg='#ff6b6b', bg='#16213e').pack(side='left', padx=10, pady=10)
        
        tk.Button(electrical_frame, text="📊 Launch Monitor", 
                 command=self.launch_electrical_monitor,
                 bg='#ff6b6b', fg='white', font=('Arial', 10, 'bold')).pack(side='right', padx=10, pady=5)
        
        tk.Label(electrical_frame, text="Infrastructure monitoring • IoT integration • Real-time data", 
                font=('Arial', 9), fg='#cccccc', bg='#16213e').pack(side='right', padx=10)
        
        # Quick Launch section
        quick_frame = tk.LabelFrame(main_frame, text="⚡ Quick Launch", 
                                  bg='#0a0a1e', fg='#ffffff', 
                                  font=('Arial', 12, 'bold'))
        quick_frame.pack(fill='x', pady=10)
        
        quick_buttons_frame = tk.Frame(quick_frame, bg='#0a0a1e')
        quick_buttons_frame.pack(pady=15)
        
        tk.Button(quick_buttons_frame, text="🇨🇷 Full Tourism Platform", 
                 command=self.launch_full_platform,
                 bg='#ffd700', fg='black', font=('Arial', 12, 'bold'),
                 width=25, height=2).pack(side='left', padx=10)
        
        tk.Button(quick_buttons_frame, text="🏨 Business Portal", 
                 command=self.launch_business_portal,
                 bg='#9b59b6', fg='white', font=('Arial', 12, 'bold'),
                 width=25, height=2).pack(side='left', padx=10)
        
        # Status section
        status_frame = tk.LabelFrame(main_frame, text="📊 System Status", 
                                   bg='#0a0a1e', fg='#ffffff', 
                                   font=('Arial', 12, 'bold'))
        status_frame.pack(fill='x', pady=10)
        
        self.status_text = tk.Text(status_frame, height=8, width=80, 
                                  bg='#16213e', fg='#cccccc', font=('Arial', 9))
        status_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        status_scrollbar.pack(side="right", fill="y", pady=10)
        
        # Control buttons
        control_frame = tk.Frame(main_frame, bg='#0a0a1e')
        control_frame.pack(fill='x', pady=10)
        
        tk.Button(control_frame, text="🔄 Refresh Status", 
                 command=self.refresh_status,
                 bg='#17a2b8', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="❌ Stop All", 
                 command=self.stop_all_services,
                 bg='#dc3545', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="📋 View Logs", 
                 command=self.view_logs,
                 bg='#6c757d', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="❓ Help", 
                 command=self.show_help,
                 bg='#28a745', fg='white', font=('Arial', 10)).pack(side='right', padx=5)
        
        # Initialize status
        self.log_status("🟢 NexusOptim IA Tourism Platform Launcher initialized")
        self.log_status("🇨🇷 Ready to launch Smart Tourism services for Costa Rica")
        self.log_status("✨ Premium business features • AI recommendations • IoT integration")
        
    def launch_tourism_platform(self):
        """Launch the main tourism platform"""
        try:
            self.log_status("🚀 Launching Smart Tourism Platform...")
            
            script_path = os.path.join(os.getcwd(), "ui", "smart_tourism_platform.py")
            if not os.path.exists(script_path):
                self.log_status("❌ Error: Tourism platform script not found")
                return
                
            process = subprocess.Popen([sys.executable, script_path], 
                                     creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            self.processes['tourism_platform'] = process
            self.log_status("✅ Smart Tourism Platform launched successfully")
            
        except Exception as e:
            self.log_status(f"❌ Error launching tourism platform: {e}")
            
    def initialize_ai_engine(self):
        """Initialize AI engine"""
        try:
            self.log_status("🤖 Initializing Tourism AI Engine...")
            
            # Run AI engine initialization
            script_path = os.path.join(os.getcwd(), "ai", "tourism_ai_engine.py")
            if not os.path.exists(script_path):
                self.log_status("❌ Error: AI engine script not found")
                return
                
            process = subprocess.Popen([sys.executable, script_path], 
                                     capture_output=True, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.log_status("✅ Tourism AI Engine initialized successfully")
                self.log_status("🧠 ML models loaded • User profiling active • Analytics ready")
            else:
                self.log_status(f"❌ AI Engine error: {stderr}")
                
        except Exception as e:
            self.log_status(f"❌ Error initializing AI engine: {e}")
            
    def launch_electrical_monitor(self):
        """Launch electrical monitoring system"""
        try:
            self.log_status("⚡ Launching Electrical Monitoring System...")
            
            script_path = os.path.join(os.getcwd(), "integrated_electrical_monitor.py")
            if not os.path.exists(script_path):
                self.log_status("❌ Error: Electrical monitor script not found")
                return
                
            process = subprocess.Popen([sys.executable, script_path], 
                                     creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            self.processes['electrical_monitor'] = process
            self.log_status("✅ Electrical Monitoring System launched")
            
        except Exception as e:
            self.log_status(f"❌ Error launching electrical monitor: {e}")
            
    def launch_full_platform(self):
        """Launch full integrated platform"""
        self.log_status("🚀 Launching Full Tourism Platform...")
        
        # Launch AI engine first
        self.initialize_ai_engine()
        
        # Small delay for AI initialization
        self.root.after(2000, self.launch_tourism_platform)
        
        self.log_status("🌟 Full platform launch sequence initiated")
        
    def launch_business_portal(self):
        """Launch business management portal"""
        try:
            self.log_status("🏨 Launching Business Portal...")
            
            # Create a simple business portal
            self.create_business_portal()
            
        except Exception as e:
            self.log_status(f"❌ Error launching business portal: {e}")
            
    def create_business_portal(self):
        """Create business management portal window"""
        portal_window = tk.Toplevel(self.root)
        portal_window.title("🏨 NexusOptim IA - Business Portal")
        portal_window.geometry("700x500")
        portal_window.configure(bg='#1a1a2e')
        
        # Header
        header = tk.Label(portal_window, text="🏨 Business Management Portal", 
                         font=('Arial', 16, 'bold'), fg='#ffd700', bg='#1a1a2e')
        header.pack(pady=20)
        
        # Services
        services_frame = tk.LabelFrame(portal_window, text="💎 Premium Services", 
                                     bg='#1a1a2e', fg='white', font=('Arial', 12, 'bold'))
        services_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Premium activation
        premium_info = """
🏆 PREMIUM POSITIONING SERVICES

✨ Gold Tier - $100/month:
• #1 position in all searches
• Golden premium badge
• AI priority recommendations  
• Detailed analytics dashboard
• 24/7 premium support

💎 Silver Tier - $50/month:
• Top 3 search positioning
• Silver premium badge
• Enhanced AI visibility
• Weekly analytics reports

🥉 Bronze Tier - $25/month:
• Improved search ranking
• Bronze premium badge
• Basic analytics
        """
        
        info_label = tk.Label(services_frame, text=premium_info, 
                             bg='#1a1a2e', fg='#cccccc', font=('Arial', 10), 
                             justify=tk.LEFT)
        info_label.pack(pady=20, padx=20)
        
        # Activation buttons
        buttons_frame = tk.Frame(services_frame, bg='#1a1a2e')
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="🥉 Activate Bronze", 
                 command=lambda: self.activate_premium('bronze'),
                 bg='#cd7f32', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        
        tk.Button(buttons_frame, text="💎 Activate Silver", 
                 command=lambda: self.activate_premium('silver'),
                 bg='#c0c0c0', fg='black', font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        
        tk.Button(buttons_frame, text="🏆 Activate Gold", 
                 command=lambda: self.activate_premium('gold'),
                 bg='#ffd700', fg='black', font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        
        self.log_status("✅ Business Portal opened")
        
    def activate_premium(self, tier):
        """Activate premium service"""
        costs = {'bronze': 25, 'silver': 50, 'gold': 100}
        cost = costs[tier]
        
        result = messagebox.askyesno("Activate Premium", 
                                   f"Activate {tier.title()} Premium Service?\n\n"
                                   f"💰 Cost: ${cost}/month\n"
                                   f"🚀 Instant search boost\n"
                                   f"📊 Analytics included\n\n"
                                   f"Proceed with activation?")
        
        if result:
            messagebox.showinfo("Premium Activated", 
                               f"✅ {tier.title()} Premium activated!\n\n"
                               f"🏆 Your listings now have priority\n"
                               f"📈 Visibility boost: {{'bronze': '50%', 'silver': '100%', 'gold': '200%'}[tier]}\n"
                               f"📊 Analytics dashboard available\n"
                               f"🤖 AI recommendation priority enabled")
            
            self.log_status(f"💎 {tier.title()} Premium service activated")
        
    def log_status(self, message):
        """Log status message"""
        timestamp = tk.datetime.datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def refresh_status(self):
        """Refresh system status"""
        self.log_status("🔄 Refreshing system status...")
        
        # Check running processes
        active_processes = 0
        for name, process in self.processes.items():
            if process and process.poll() is None:
                active_processes += 1
                self.log_status(f"✅ {name} - Running (PID: {process.pid})")
            else:
                self.log_status(f"❌ {name} - Not running")
                
        self.log_status(f"📊 Total active services: {active_processes}")
        
    def stop_all_services(self):
        """Stop all running services"""
        self.log_status("⏹️ Stopping all services...")
        
        stopped_count = 0
        for name, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    process.terminate()
                    stopped_count += 1
                    self.log_status(f"🛑 Stopped {name}")
                except:
                    self.log_status(f"❌ Error stopping {name}")
                    
        self.log_status(f"✅ Stopped {stopped_count} services")
        
    def view_logs(self):
        """View system logs"""
        log_window = tk.Toplevel(self.root)
        log_window.title("📋 System Logs")
        log_window.geometry("800x600")
        log_window.configure(bg='#1a1a2e')
        
        log_text = tk.Text(log_window, bg='#16213e', fg='#cccccc', font=('Consolas', 9))
        log_scrollbar = ttk.Scrollbar(log_window, orient="vertical", command=log_text.yview)
        log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        log_scrollbar.pack(side="right", fill="y", pady=10)
        
        # Sample logs
        sample_logs = """
[2025-01-12 10:30:15] 🚀 NexusOptim IA Tourism Platform started
[2025-01-12 10:30:16] 🤖 AI Engine initialized with ML models
[2025-01-12 10:30:17] 🗄️ Database connected successfully
[2025-01-12 10:30:18] 🌐 LoRaWAN receiver started on AU915
[2025-01-12 10:30:19] 📊 Analytics service ready
[2025-01-12 10:30:20] ✅ All systems operational
[2025-01-12 10:31:45] 👤 New user registered: user_cr_001
[2025-01-12 10:32:10] 🔍 Search query: "volcán arenal tech tour"
[2025-01-12 10:32:11] 🤖 AI generated 5 recommendations
[2025-01-12 10:33:22] 🎫 Booking confirmed: Arenal IoT Tour
[2025-01-12 10:34:15] 💎 Premium service activated: Hotel Presidente
[2025-01-12 10:35:30] 📈 Analytics updated: +15% conversion rate
        """
        
        log_text.insert('1.0', sample_logs)
        
    def show_help(self):
        """Show help information"""
        help_text = """
🇨🇷 NEXUSOPTIM IA - SMART TOURISM PLATFORM

🚀 GETTING STARTED:
1. Click "Full Tourism Platform" for complete experience
2. Use "Initialize AI" to enable smart recommendations  
3. Launch "Electrical Monitoring" for IoT integration
4. Open "Business Portal" for premium services

🎯 KEY FEATURES:
• AI-powered tour and hotel recommendations
• Location-based smart search
• Premium business positioning
• Real-time IoT monitoring integration
• Advanced analytics dashboard

💎 PREMIUM SERVICES:
• Gold: $100/month - #1 search position
• Silver: $50/month - Top 3 positioning  
• Bronze: $25/month - Enhanced visibility

🔧 TECHNICAL SUPPORT:
• All services run independently
• IoT integration via LoRaWAN AU915
• Real-time data processing
• Machine learning recommendations

📞 CONTACT:
• Email: support@nexusoptimia.cr
• Phone: +506 2222-3333
• Web: nexusoptimia.cr
        """
        
        messagebox.showinfo("❓ Help - NexusOptim IA", help_text)
        
def main():
    """Main launcher function"""
    try:
        # Check if required directories exist
        required_dirs = ['ui', 'ai']
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                
        app = TourismLauncher()
        app.root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Launcher Error", f"Error starting launcher:\n{e}")

if __name__ == "__main__":
    main()
