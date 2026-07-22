import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { login, error } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Attempt login via API
    const success = await login(email, password);
    
    if (success) {
      setIsSuccess(true);
      // Wait a moment so the user sees the green "Authenticated" state before redirect
      setTimeout(() => {
        // Redirection is handled by the AuthContext, but we hold the state briefly
      }, 1000);
    } else {
      setIsSubmitting(false);
    }
  };

  // Button styling logic to exactly match the vanilla JS manipulation
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
      <main className="w-full h-screen md:h-[min(800px,90vh)] max-w-[1200px] flex overflow-hidden md:rounded-xl md:shadow-lg bg-surface border border-outline-variant">
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
          {/* Background Image with detail prompt */}
          <div className="absolute bottom-0 right-0 w-full h-full opacity-40 mix-blend-overlay pointer-events-none">
            <div className="w-full h-full bg-cover bg-center" style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuBBFsukOWlM7UrCbXVjEiwjQuItALBEKjjxX5H5QnJGAIIMBMECbFzNGr9Wyb9PGUEDUIsRm09yuJ17sS3RxxPmBc5sQpiZxbaJdEDdG7XDTlrBm1AhOKOqyyTh-a06vFNeJTinEsCHLtYPrdJn0hFOWGhob_Xso4SiIn81nukOVY3KD3xb8P1b2mSM4VeP9eDHzdAkI8fzOvtJAC-5wg94W06SQq70bg9Nu38kk2HFdBsT8IjOfS3L')" }}></div>
          </div>
        </section>
        
        {/* Right Side: Login Form */}
        <section className="w-full lg:w-1/2 flex flex-col items-center justify-center p-xl bg-surface relative">
          {/* Mobile Logo (Visible only on small screens) */}
          <div className="lg:hidden flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto mb-xl absolute top-md left-md">
            <span className="material-symbols-outlined text-primary text-headline-md">local_shipping</span>
            <h1 className="font-headline-md text-headline-md font-extrabold text-primary">TransitOps</h1>
          </div>
          <div className="w-full max-w-[400px]">
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
                    className="w-full h-[48px] pl-[44px] pr-md bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-md text-body-md focus:ring-2 focus:ring-primary/20 outline-none" 
                    id="password" 
                    placeholder="••••••••" 
                    required 
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
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
