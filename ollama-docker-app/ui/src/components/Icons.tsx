import React from 'react';

export const UserIcon: React.FC<{ className?: string }> = ({ className }) => (
    <div className={`flex items-center justify-center w-8 h-8 rounded-full bg-slate-700 text-white font-bold text-sm flex-shrink-0 ${className}`}>
        Me
    </div>
);

export const AiIcon: React.FC<{ className?: string }> = ({ className }) => (
    <div className={`flex items-center justify-center w-8 h-8 rounded-full bg-slate-700 text-white font-bold text-sm flex-shrink-0 ${className}`}>
        AI
    </div>
);

export const SendIcon: React.FC<{ className?: string }> = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}>
        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
    </svg>
);

export const StopIcon: React.FC<{ className?: string }> = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}>
        <path d="M6 6h12v12H6z" />
    </svg>
);