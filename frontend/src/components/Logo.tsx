import React from 'react';

export default function Logo({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg 
      viewBox="0 0 32 32" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="cloud-gradient" x1="2" y1="10" x2="30" y2="28" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#3B82F6" />
          <stop offset="100%" stopColor="#06B6D4" />
        </linearGradient>
      </defs>
      <path
        d="M25 12C25 7.58172 21.4183 4 17 4C13.6266 4 10.7483 6.09138 9.5447 9.15767C9.3755 9.1388 9.19176 9.125 9 9.125C4.85786 9.125 1.5 12.4829 1.5 16.625C1.5 20.7671 4.85786 24.125 9 24.125H24.5C27.8137 24.125 30.5 21.4387 30.5 18.125C30.5 14.8113 27.8137 12.125 24.5 12.125C24.6652 12.0837 24.8316 12.0419 25 12Z"
        fill="url(#cloud-gradient)"
        fillOpacity="0.2"
      />
      <path
        d="M9.5447 9.15767C10.7483 6.09138 13.6266 4 17 4C21.4183 4 25 7.58172 25 12C24.8316 12.0419 24.6652 12.0837 24.5 12.125C27.8137 12.125 30.5 14.8113 30.5 18.125C30.5 21.4387 27.8137 24.125 24.5 24.125H9C4.85786 24.125 1.5 20.7671 1.5 16.625C1.5 12.4829 4.85786 9.125 9 9.125"
        stroke="url(#cloud-gradient)"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M11 16L15 20L23 11"
        stroke="url(#cloud-gradient)"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
