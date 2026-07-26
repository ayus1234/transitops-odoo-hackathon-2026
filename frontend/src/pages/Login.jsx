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

  // Demo Accounts state and mode detection
  const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true' || import.meta.env.VITE_DEMO_MODE === true;
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
  let buttonClasses = "group w-full h-[48px] text-on-primary font-title-sm text-title-sm rounded-lg transition-all flex items-center justify-center gap-sm shadow-sm active:scale-[0.98]";
  if (isSuccess) {
    buttonClasses += " bg-secondary";
  } else if (isSubmitting) {
    buttonClasses += " bg-primary opacity-80 cursor-wait";
  } else {
    buttonClasses += " bg-primary hover:bg-primary-container";
  }

  return (
    <div className="text-on-surface bg-background min-h-screen flex items-center justify-center p-0 md:p-lg">
      <main className="w-full h-screen md:h-[min(840px,92vh)] max-w-[1200px] flex overflow-hidden md:rounded-xl md:shadow-lg bg-surface border border-outline-variant">
        {/* Left Side: Logistics Branding & Visual */}
        <section className="hidden lg:flex flex-col w-1/2 relative bg-primary-container text-on-primary-container p-xl overflow-hidden">
          {/* Subtle Overlay Pattern */}
          <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)", backgroundSize: "24px 24px" }}></div>
          <div className="relative z-10 flex flex-col h-full justify-between">
            <div>
              <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto mb-xl">
                <span className="material-symbols-outlined text-[32px] text-on-primary-container">local_shipping</span>
                <h1 className="font-headline-md text-headline-md font-extrabold tracking-tight">TransitOps</h1>
              </div>
              <h2 className="font-display-lg text-display-lg mb-md leading-tight">Mastering Fleet <br/>Intelligence.</h2>
              <p className="font-body-md text-body-md text-on-primary-container/80 max-w-[320px]">
                The enterprise-grade solution for real-time logistics, driver management, and global fleet optimization.
              </p>
            </div>
            <div className="mt-auto">
              <div className="p-md bg-white/10 backdrop-blur-md rounded-lg border border-white/20">
                <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto mb-xs">
                  <span className="material-symbols-outlined text-secondary-fixed">verified</span>
                  <span className="font-label-caps text-label-caps uppercase tracking-widest text-on-primary-container/90">System Status: Operational</span>
                </div>
                <p className="font-body-sm text-body-sm">All nodes active. Optimized routing for 4,200+ active units.</p>
              </div>
            </div>
          </div>
          {/* Background Image */}
          <div className="absolute bottom-0 right-0 w-full h-full opacity-40 mix-blend-overlay pointer-events-none">
            <div className="w-full h-full bg-cover bg-center" style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuBBFsukOWlM7UrCbXVjEiwjQuItALBEKjjxX5H5QnJGAIIMBMECbFzNGr9Wyb9PGUEDUIsRm09yuJ17sS3RxxPmBc5sQpiZxbaJdEDdG7XDTlrBm1AhOKOqyyTh-a06vFNeJTinEsCHLtYPrdJn0hFOWGhob_Xso4SiIn81nukOVY3KD3xb8P1b2mSM4VeP9eDHzdAkI8fzOvtJAC-5wg94W06SQq70bg9Nu38kk2HFdBsT8IjOfS3L')" }}></div>
          </div>
        </section>
        
        {/* Right Side: Login Form & Demo Accounts */}
        <section className="w-full lg:w-1/2 flex flex-col items-center justify-center p-md sm:p-lg md:p-xl bg-surface relative overflow-y-auto max-h-screen">
          <div className="w-full max-w-[420px] my-auto py-6">
            {/* Mobile Logo (Visible only on small screens) */}
            <div className="lg:hidden flex items-center gap-sm mb-lg">
              <span className="material-symbols-outlined text-primary text-headline-md">local_shipping</span>
              <h1 className="font-headline-md text-headline-md font-extrabold text-primary">TransitOps</h1>
            </div>
            
            <header className="mb-xl">
              <h2 className="font-headline-md text-headline-md text-on-surface mb-xs">Welcome Back</h2>
              <p className="font-body-md text-body-md text-on-surface-variant">Access your logistics control center</p>
            </header>
            
            {error && (
              <div className="mb-4 p-3 bg-error-container text-on-error-container text-sm rounded border border-error/20 flex items-center gap-2">
                <span className="material-symbols-outlined">error</span>
                {error}
              </div>
            )}

            {/* Role-Based Demo Login Selector */}
            {isDemoMode && (
              <div className="mb-lg space-y-md">
                <div className="space-y-xs">
                  <label className="font-body-sm text-body-sm font-bold text-on-surface flex items-center gap-1.5" htmlFor="role-select">
                    <span className="material-symbols-outlined text-[18px] text-primary">science</span>
                    <span>Login As</span>
                  </label>
                  <div className="relative group">
                    <select
                      id="role-select"
                      aria-label="Login As"
                      value={selectedRoleName}
                      onChange={handleRoleChange}
                      className="w-full h-[48px] pl-md pr-[40px] bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-md text-body-md focus:ring-2 focus:ring-primary/20 outline-none appearance-none cursor-pointer text-on-surface font-medium"
                    >
                      <option value="">Select a demo role</option>
                      {demoAccounts.map((acct) => (
                        <option key={acct.role} value={acct.role}>
                          {acct.role}
                        </option>
                      ))}
                    </select>
                    <span className="material-symbols-outlined absolute right-md top-1/2 -translate-y-1/2 text-outline pointer-events-none text-[20px] group-focus-within:text-primary transition-colors">
                      expand_more
                    </span>
                  </div>
                </div>

                {selectedAccount && (
                  <div className="p-4 bg-primary-container/15 border border-primary/25 rounded-lg space-y-3 shadow-2xs transition-all animate-fadeIn">
                    <div className="flex items-center justify-between border-b border-primary/15 pb-2">
                      <div className="flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-primary text-[18px]">vpn_key</span>
                        <h3 className="font-title-sm font-bold text-on-surface text-sm">
                          {selectedAccount.role} Demo Access
                        </h3>
                      </div>
                    </div>

                    <div className="space-y-2 text-xs">
                      {/* Login ID */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2.5 bg-surface rounded border border-outline-variant/60">
                        <div className="flex flex-col min-w-0 mr-2">
                          <span className="text-on-surface-variant font-medium text-[10px] uppercase tracking-wider">Login ID</span>
                          <span className="font-mono text-[12px] font-semibold text-on-surface truncate" title={selectedAccount.email}>
                            {selectedAccount.email}
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleCopy(selectedAccount.email, 'email')}
                          className="shrink-0 px-2.5 py-1.5 bg-surface-variant/40 hover:bg-surface-variant border border-outline-variant/80 text-on-surface-variant hover:text-on-surface rounded text-[11px] font-semibold transition-all flex items-center gap-1 active:scale-[0.98] self-start sm:self-auto"
                          aria-label={`Copy ${selectedAccount.role} login ID`}
                        >
                          <span className="material-symbols-outlined text-[14px]">
                            {copiedField === 'email' ? 'check' : 'content_copy'}
                          </span>
                          <span>{copiedField === 'email' ? 'Copied' : 'Copy'}</span>
                        </button>
                      </div>

                      {/* Password */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2.5 bg-surface rounded border border-outline-variant/60">
                        <div className="flex items-center justify-between sm:justify-start gap-3 min-w-0 flex-1">
                          <div className="flex flex-col min-w-0">
                            <span className="text-on-surface-variant font-medium text-[10px] uppercase tracking-wider">Password</span>
                            <span className="font-mono text-[12px] font-semibold text-on-surface tracking-wider">
                              {showDemoPassword ? selectedAccount.password : '••••••••'}
                            </span>
                          </div>
                          <button
                            type="button"
                            onClick={() => setShowDemoPassword((prev) => !prev)}
                            className="text-outline hover:text-primary transition-colors p-1.5 rounded hover:bg-surface-variant/30 focus:outline-none focus:ring-1 focus:ring-primary/20 flex items-center justify-center shrink-0"
                            aria-label={showDemoPassword ? "Hide password" : "Show password"}
                          >
                            <span className="material-symbols-outlined text-[18px]">
                              {showDemoPassword ? "visibility_off" : "visibility"}
                            </span>
                          </button>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleCopy(selectedAccount.password, 'password')}
                          className="shrink-0 px-2.5 py-1.5 bg-surface-variant/40 hover:bg-surface-variant border border-outline-variant/80 text-on-surface-variant hover:text-on-surface rounded text-[11px] font-semibold transition-all flex items-center gap-1 active:scale-[0.98] self-start sm:self-auto"
                          aria-label={`Copy ${selectedAccount.role} demo password`}
                        >
                          <span className="material-symbols-outlined text-[14px]">
                            {copiedField === 'password' ? 'check' : 'content_copy'}
                          </span>
                          <span>{copiedField === 'password' ? 'Copied' : 'Copy'}</span>
                        </button>
                      </div>
                    </div>

                    <div className="pt-1 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                      <p className="font-body-xs text-[12px] text-on-surface-variant leading-snug pr-2">
                        Use these credentials to access the {selectedAccount.role} workspace.
                      </p>
                      <button
                        type="button"
                        onClick={() => handleUseCredentials(selectedAccount)}
                        className="w-full sm:w-auto shrink-0 px-3 py-2 bg-primary/10 hover:bg-primary text-primary hover:text-on-primary border border-primary/25 rounded-lg text-[12px] font-bold transition-all flex items-center justify-center gap-1.5 shadow-2xs active:scale-[0.98]"
                      >
                        <span className="material-symbols-outlined text-[16px]">login</span>
                        <span>Use Credentials</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            <form className="space-y-lg" id="loginForm" onSubmit={handleLogin}>
              {/* Email Field */}
              <div className="space-y-xs">
                <label className="font-body-sm text-body-sm font-bold text-on-surface" htmlFor="email">Email Address</label>
                <div className="relative group">
                  <span className="absolute left-md top-1/2 -translate-y-1/2 material-symbols-outlined text-outline text-[20px] group-focus-within:text-primary transition-colors">mail</span>
                  <input 
                    className="w-full h-[48px] pl-[44px] pr-md bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-md text-body-md focus:ring-2 focus:ring-primary/20 outline-none" 
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
              <div className="space-y-xs">
                <div className="flex justify-between items-center">
                  <label className="font-body-sm text-body-sm font-bold text-on-surface" htmlFor="password">Password</label>
                  <a className="font-body-sm text-body-sm text-primary hover:underline transition-all" href="#">Forgot password?</a>
                </div>
                <div className="relative group">
                  <span className="absolute left-md top-1/2 -translate-y-1/2 material-symbols-outlined text-outline text-[20px] group-focus-within:text-primary transition-colors">lock</span>
                  <input 
                    className="w-full h-[48px] pl-[44px] pr-[48px] bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-md text-body-md focus:ring-2 focus:ring-primary/20 outline-none" 
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
                    className="absolute right-md top-1/2 -translate-y-1/2 text-outline hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 rounded p-1 flex items-center justify-center"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    <span className="material-symbols-outlined text-[20px]">
                      {showPassword ? "visibility_off" : "visibility"}
                    </span>
                  </button>
                </div>
              </div>
              {/* Remember Me & Policy */}
              <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
                <input className="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary/20 cursor-pointer" id="remember" type="checkbox"/>
                <label className="font-body-sm text-body-sm text-on-surface-variant cursor-pointer select-none" htmlFor="remember">
                  Keep me logged in for 30 days
                </label>
              </div>
              {/* Login Button */}
              <button 
                className={buttonClasses} 
                type="submit"
                disabled={isSubmitting || isSuccess}
              >
                {isSuccess ? (
                  <>
                    <span className="material-symbols-outlined">check</span>
                    <span>Authenticated</span>
                  </>
                ) : isSubmitting ? (
                  <>
                    <span className="material-symbols-outlined animate-spin">progress_activity</span>
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In</span>
                    <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform">arrow_forward</span>
                  </>
                )}
              </button>
            </form>

            <footer className="mt-xl pt-xl border-t border-outline-variant text-center">
              <p className="font-body-sm text-body-sm text-on-surface-variant mb-md">
                Protected by enterprise-grade security.
              </p>
              <div className="flex justify-center gap-xl grayscale opacity-50">
                <div className="flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[18px]">security</span>
                  <span className="font-label-caps text-label-caps uppercase">ISO 27001</span>
                </div>
                <div className="flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[18px]">shield</span>
                  <span className="font-label-caps text-label-caps uppercase">SOC 2 Type II</span>
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
