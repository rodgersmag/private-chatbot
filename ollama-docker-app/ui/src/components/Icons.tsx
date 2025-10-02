import React from 'react';

export const UserIcon: React.FC<{ className?: string }> = ({ className }) => (
    <div className={`flex items-center justify-center w-8 h-8 rounded-full bg-slate-700 text-white font-bold text-sm flex-shrink-0 ${className}`}>
        Me
    </div>
);

export const AiIcon: React.FC<{ className?: string }> = ({ className }) => (
    <div className={`flex items-center justify-center w-8 h-8 rounded-full bg-slate-700 text-white flex-shrink-0 ${className}`}>
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
            <path fill="none" d="M0 0h24v24H0z"/><path d="M19.49 5.51A9.956 9.956 0 0 0 12 2C6.48 2 2 6.48 2 12s4.48 10 10 10a9.983 9.983 0 0 0 7.49-3.51L12 12l7.49-6.49zM12 20c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-2-9h4v2h-4v-2zm-2-4h8v2H8V7z"/>
        </svg>
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