import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const DEFAULT_DEMO_ACCOUNTS = [
  {
    role: "Super Admin",
    email: "admin@transitops.com",
    password: "admin123",
    description: "Unrestricted administrative access across all enterprise ERP modules, user management, and system governance."
  },
  {
    role: "Administrator",
    email: "administrator@transitops.com",
    password: "adminpass2026",
    description: "Comprehensive administrative privileges for configuring roles, organization settings, and enterprise oversight."
  },
  {
    role: "System Admin",
    email: "sysadmin@transitops.com",
    password: "sysadmin2026",
    description: "Technical administrative control over system diagnostics, support center operations, and server configurations."
  },
  {
    role: "Fleet Manager",
    email: "fleet@transitops.com",
    password: "fleet2026",
    description: "Full fleet management capabilities including vehicle registry, driver assignments, trip tracking, and operational reports."
  },
  {
    role: "Dispatcher",
    email: "dispatcher@transitops.com",
    password: "dispatch2026",
    description: "Operational control over trip creation, route scheduling, driver assignments, and live dispatch monitoring."
  },
  {
    role: "Maintenance Manager",
    email: "maintenance@transitops.com",
    password: "maint2026",
    description: "Authority over vehicle servicing, repair schedules, maintenance approval workflows, and part inventory management."
  },
  {
    role: "Technician",
    email: "technician@transitops.com",
    password: "tech2026",
    description: "Field access to inspect vehicles, log repair notes, update task statuses, and monitor service checklists."
  },
  {
    role: "Safety Officer",
    email: "safety@transitops.com",
    password: "safety2026",
    description: "Focused access to driver safety scores, incident logs, compliance audits, and enterprise safety analytics."
  },
  {
    role: "Financial Analyst",
    email: "finance@transitops.com",
    password: "finance123",
    description: "Comprehensive financial insight across expenses, fuel budgeting, operational cost analytics, and accounting reports."
  },
  {
    role: "Procurement Operations",
    email: "procurement@transitops.com",
    password: "procure2026",
    description: "Management of inventory ordering, vendor purchase orders, spare parts requisition, and cost approvals."
  },
  {
    role: "HR/Operations",
    email: "hr@transitops.com",
    password: "hr2026",
    description: "Personnel management access for driver onboarding, profile updates, license verification, and HR records."
  },
  {
    role: "Support Agent",
    email: "support@transitops.com",
    password: "support2026",
    description: "Help center access to resolve user tickets, assist driver technical issues, and log support interactions."
  },
  {
    role: "Driver",
    email: "driver@transitops.com",
    password: "driver2026",
    description: "Driver portal access for viewing assigned trips, vehicle telemetry, navigation logs, and personal safety metrics."
  }
];

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { login, error } = useAuth();

  // Demo Accounts state and mode detection (defaults to true for hackathon evaluation unless explicitly disabled)
  const isDemoMode = import.meta.env.VITE_DEMO_MODE !== 'false' && import.meta.env.VITE_DEMO_MODE !== false;
  const [demoAccounts, setDemoAccounts] = useState(DEFAULT_DEMO_ACCOUNTS);
  const [selectedRoleName, setSelectedRoleName] = useState('');
  const [showDemoPassword, setShowDemoPassword] = useState(false);
  const [copiedField, setCopiedField] = useState('');

  useEffect(() => {
    if (isDemoMode) {
      api.get('/auth/demo-accounts')
        .then((response) => {
          if (Array.isArray(response.data) && response.data.length > 0) {
            setDemoAccounts(response.data);
          }
        })
        .catch(() => {
          // Fallback to DEFAULT_DEMO_ACCOUNTS if API is unavailable during offline viewing
        });
    }
  }, [isDemoMode]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Attempt login via API (normal JWT authentication)
    const success = await login(email, password);
    
    if (success) {
      setIsSuccess(true);
      setTimeout(() => {
        // Redirection handled by AuthContext
      }, 1000);
    } else {
      setIsSubmitting(false);
    }
  };

  const selectedAccount = demoAccounts.find((a) => a.role === selectedRoleName);

  const handleRoleChange = (e) => {
    setSelectedRoleName(e.target.value);
    setShowDemoPassword(false);
    setCopiedField('');
    setEmail('');
    setPassword('');
  };

  const handleCopy = (text, fieldName) => {
    if (navigator?.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedField(fieldName);
      setTimeout(() => setCopiedField(''), 2000);
    }
  };

  const handleUseCredentials = (account) => {
    setEmail(account.email);
    setPassword(account.password);
    const emailInput = document.getElementById('email');
    if (emailInput) {
      emailInput.focus();
    }
  };

  // Button styling logic
  let buttonClasses = "group w-full h-[44px] text-on-primary font-title-sm text-sm font-bold rounded-lg transition-all flex items-center justify-center gap-2 shadow-sm active:scale-[0.98]";
  if (isSuccess) {
    buttonClasses += " bg-secondary";
  } else if (isSubmitting) {
    buttonClasses += " bg-primary opacity-80 cursor-wait";
  } else {
    buttonClasses += " bg-primary hover:bg-primary-container hover:text-on-primary-container";
  }

  return (
    <div className="text-on-surface bg-background min-h-screen w-full flex justify-center py-6 px-3 sm:py-8 sm:px-6 md:px-8 overflow-y-auto">
      <main className="w-full max-w-[1150px] my-auto flex flex-col lg:flex-row rounded-xl shadow-2xl bg-surface border border-outline-variant overflow-hidden">
        {/* Left Side: Logistics Branding & Visual */}
        <section className="hidden lg:flex flex-col w-1/2 relative bg-primary-container text-on-primary-container p-8 xl:p-12 overflow-hidden justify-between min-h-[560px]">
          {/* Subtle Overlay Pattern */}
          <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)", backgroundSize: "24px 24px" }}></div>
          <div className="relative z-10 flex flex-col h-full justify-between">
            <div>
              <div className="flex items-center gap-2 mb-8">
                <span className="material-symbols-outlined text-[32px] text-on-primary-container">local_shipping</span>
                <h1 className="text-2xl xl:text-3xl font-extrabold tracking-tight">TransitOps</h1>
              </div>
              <h2 className="text-3xl xl:text-4xl font-extrabold mb-4 leading-tight">Mastering Fleet <br/>Intelligence.</h2>
              <p className="text-sm xl:text-base text-on-primary-container/85 max-w-[340px] leading-relaxed">
                The enterprise-grade solution for real-time logistics, driver management, and global fleet optimization.
              </p>
            </div>
            <div className="mt-8">
              <div className="p-4 bg-white/10 backdrop-blur-md rounded-lg border border-white/20">
                <div className="flex items-center gap-2 mb-1">
                  <span className="material-symbols-outlined text-secondary-fixed text-[20px]">verified</span>
                  <span className="text-[11px] uppercase font-bold tracking-widest text-on-primary-container/95">System Status: Operational</span>
                </div>
                <p className="text-xs xl:text-sm text-on-primary-container/90">All nodes active. Optimized routing for 4,200+ active units.</p>
              </div>
            </div>
          </div>
          {/* Background Image */}
          <div className="absolute bottom-0 right-0 w-full h-full opacity-40 mix-blend-overlay pointer-events-none">
            <div className="w-full h-full bg-cover bg-center" style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuBBFsukOWlM7UrCbXVjEiwjQuItALBEKjjxX5H5QnJGAIIMBMECbFzNGr9Wyb9PGUEDUIsRm09yuJ17sS3RxxPmBc5sQpiZxbaJdEDdG7XDTlrBm1AhOKOqyyTh-a06vFNeJTinEsCHLtYPrdJn0hFOWGhob_Xso4SiIn81nukOVY3KD3xb8P1b2mSM4VeP9eDHzdAkI8fzOvtJAC-5wg94W06SQq70bg9Nu38kk2HFdBsT8IjOfS3L')" }}></div>
          </div>
        </section>
        
        {/* Right Side: Login Form & Demo Accounts */}
        <section className="w-full lg:w-1/2 flex flex-col justify-center p-6 sm:p-8 md:p-10 bg-surface relative">
          <div className="w-full max-w-[440px] mx-auto py-2">
            {/* Mobile Logo (Visible only on small screens) */}
            <div className="lg:hidden flex items-center gap-2 mb-6">
              <span className="material-symbols-outlined text-primary text-2xl">local_shipping</span>
              <h1 className="text-2xl font-extrabold text-primary">TransitOps</h1>
            </div>
            
            <header className="mb-5">
              <h2 className="text-2xl font-extrabold text-on-surface mb-1">Welcome Back</h2>
              <p className="text-sm text-on-surface-variant">Access your logistics control center</p>
            </header>
            
            {error && (
              <div className="mb-4 p-3 bg-error-container text-on-error-container text-xs rounded-lg border border-error/20 flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">error</span>
                {error}
              </div>
            )}

            {/* Role-Based Demo Login Selector */}
            {isDemoMode && (
              <div className="mb-5 space-y-3">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-on-surface flex items-center gap-1.5" htmlFor="role-select">
                    <span className="material-symbols-outlined text-[17px] text-primary">science</span>
                    <span>Login As</span>
                  </label>
                  <div className="relative group">
                    <select
                      id="role-select"
                      aria-label="Login As"
                      value={selectedRoleName}
                      onChange={handleRoleChange}
                      className="w-full h-[42px] pl-3 pr-8 bg-surface border border-outline-variant rounded-lg focus:border-primary transition-all text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none appearance-none cursor-pointer text-on-surface"
                    >
                      <option value="">Select a demo role</option>
                      {demoAccounts.map((acct) => (
                        <option key={acct.role} value={acct.role}>
                          {acct.role}
                        </option>
                      ))}
                    </select>
                    <span className="material-symbols-outlined absolute right-2.5 top-1/2 -translate-y-1/2 text-outline pointer-events-none text-[20px] group-focus-within:text-primary transition-colors">
                      expand_more
                    </span>
                  </div>
                </div>

                {selectedAccount && (
                  <div className="p-3.5 bg-primary-container/15 border border-primary/25 rounded-xl space-y-3 shadow-2xs transition-all animate-fadeIn">
                    <div className="flex items-center justify-between border-b border-primary/15 pb-2.5">
                      <div className="flex items-center gap-1.5 min-w-0 mr-2">
                        <span className="material-symbols-outlined text-primary text-[18px] shrink-0">vpn_key</span>
                        <h3 className="font-title-sm font-bold text-on-surface text-xs sm:text-sm truncate">
                          {selectedAccount.role} Demo Access
                        </h3>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleUseCredentials(selectedAccount)}
                        className="shrink-0 px-2.5 py-1.5 bg-primary hover:bg-primary/90 text-on-primary rounded-lg text-[11px] font-bold transition-all flex items-center gap-1 shadow-2xs active:scale-[0.98]"
                      >
                        <span className="material-symbols-outlined text-[15px]">login</span>
                        <span>Use Credentials</span>
                      </button>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                      {/* Login ID */}
                      <div className="flex items-center justify-between gap-2 p-2 bg-surface rounded-lg border border-outline-variant/70">
                        <div className="flex flex-col min-w-0 mr-1 flex-1">
                          <span className="text-on-surface-variant font-semibold text-[9px] uppercase tracking-wider">Login ID</span>
                          <span className="font-mono text-[11px] font-bold text-on-surface truncate" title={selectedAccount.email}>
                            {selectedAccount.email}
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleCopy(selectedAccount.email, 'email')}
                          className="shrink-0 px-2 py-1 bg-surface-variant/40 hover:bg-surface-variant border border-outline-variant/80 text-on-surface-variant hover:text-on-surface rounded text-[10px] font-semibold transition-all flex items-center gap-0.5 active:scale-[0.98]"
                          aria-label={`Copy ${selectedAccount.role} login ID`}
                        >
                          <span className="material-symbols-outlined text-[13px]">
                            {copiedField === 'email' ? 'check' : 'content_copy'}
                          </span>
                          <span>{copiedField === 'email' ? 'Copied' : 'Copy'}</span>
                        </button>
                      </div>

                      {/* Password */}
                      <div className="flex items-center justify-between gap-2 p-2 bg-surface rounded-lg border border-outline-variant/70">
                        <div className="flex items-center justify-between min-w-0 flex-1 gap-1">
                          <div className="flex flex-col min-w-0 flex-1">
                            <span className="text-on-surface-variant font-semibold text-[9px] uppercase tracking-wider">Password</span>
                            <span className="font-mono text-[11px] font-bold text-on-surface truncate tracking-wider">
                              {showDemoPassword ? selectedAccount.password : '••••••••'}
                            </span>
                          </div>
                          <button
                            type="button"
                            onClick={() => setShowDemoPassword((prev) => !prev)}
                            className="text-outline hover:text-primary transition-colors p-1 rounded hover:bg-surface-variant/30 focus:outline-none focus:ring-1 focus:ring-primary/20 flex items-center justify-center shrink-0"
                            aria-label={showDemoPassword ? "Hide password" : "Show password"}
                          >
                            <span className="material-symbols-outlined text-[16px]">
                              {showDemoPassword ? "visibility_off" : "visibility"}
                            </span>
                          </button>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleCopy(selectedAccount.password, 'password')}
                          className="shrink-0 px-2 py-1 bg-surface-variant/40 hover:bg-surface-variant border border-outline-variant/80 text-on-surface-variant hover:text-on-surface rounded text-[10px] font-semibold transition-all flex items-center gap-0.5 active:scale-[0.98]"
                          aria-label={`Copy ${selectedAccount.role} demo password`}
                        >
                          <span className="material-symbols-outlined text-[13px]">
                            {copiedField === 'password' ? 'check' : 'content_copy'}
                          </span>
                          <span>{copiedField === 'password' ? 'Copied' : 'Copy'}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            <form className="space-y-4" id="loginForm" onSubmit={handleLogin}>
              {/* Email Field */}
              <div className="space-y-1">
                <label className="text-xs font-bold text-on-surface" htmlFor="email">Email Address</label>
                <div className="relative group">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-outline text-[18px] group-focus-within:text-primary transition-colors">mail</span>
                  <input 
                    className="w-full h-[42px] pl-9 pr-3 bg-surface border border-outline-variant rounded-lg focus:border-primary transition-all text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none" 
                    id="email" 
                    placeholder="name@company.com" 
                    required 
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>
              {/* Password Field */}
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold text-on-surface" htmlFor="password">Password</label>
                  <a className="text-xs text-primary font-medium hover:underline transition-all" href="#">Forgot password?</a>
                </div>
                <div className="relative group">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-outline text-[18px] group-focus-within:text-primary transition-colors">lock</span>
                  <input 
                    className="w-full h-[42px] pl-9 pr-9 bg-surface border border-outline-variant rounded-lg focus:border-primary transition-all text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none" 
                    id="password" 
                    placeholder="••••••••" 
                    required 
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-outline hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 rounded p-1 flex items-center justify-center"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    <span className="material-symbols-outlined text-[18px]">
                      {showPassword ? "visibility_off" : "visibility"}
                    </span>
                  </button>
                </div>
              </div>
              {/* Remember Me & Policy */}
              <div className="flex items-center gap-2 pt-0.5">
                <input className="w-3.5 h-3.5 rounded border-outline-variant text-primary focus:ring-primary/20 cursor-pointer" id="remember" type="checkbox"/>
                <label className="text-xs text-on-surface-variant cursor-pointer select-none font-medium" htmlFor="remember">
                  Keep me logged in for 30 days
                </label>
              </div>
              {/* Login Button */}
              <div className="pt-1">
                <button 
                  className={buttonClasses} 
                  type="submit"
                  disabled={isSubmitting || isSuccess}
                >
                  {isSuccess ? (
                    <>
                      <span className="material-symbols-outlined text-[18px]">check</span>
                      <span>Authenticated</span>
                    </>
                  ) : isSubmitting ? (
                    <>
                      <span className="material-symbols-outlined text-[18px] animate-spin">progress_activity</span>
                      <span>Authenticating...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In</span>
                      <span className="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                    </>
                  )}
                </button>
              </div>
            </form>

            <footer className="mt-6 pt-4 border-t border-outline-variant/60 text-center">
              <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-[11px] text-on-surface-variant/80 font-medium">
                <span>Protected by enterprise security</span>
                <span className="hidden sm:inline text-outline-variant">•</span>
                <div className="flex items-center gap-3 grayscale opacity-65">
                  <div className="flex items-center gap-1">
                    <span className="material-symbols-outlined text-[14px]">security</span>
                    <span className="font-bold uppercase tracking-wider">ISO 27001</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="material-symbols-outlined text-[14px]">shield</span>
                    <span className="font-bold uppercase tracking-wider">SOC 2 Type II</span>
                  </div>
                </div>
              </div>
            </footer>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Login;
