import React, { useState } from 'react';
import { Stack } from 'expo-router';
import LoginScreen from './login';
import LoadingScreen from './loading';
import GuestFlightsScreen from './guest-flight';

export default function RootLayout() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGuest, setIsGuest] = useState(false);

  const handleLogin = (ticketNumber: string, flightNumber: string) => {
    setIsLoading(true);
    
    // Check if it's a guest login (both are empty strings)
    const guestLogin = ticketNumber === '' && flightNumber === '';
    
    setTimeout(() => {
      setIsLoading(false);
      setIsAuthenticated(true);
      setIsGuest(guestLogin);
    }, 2000);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setIsGuest(false);
  };

  if (!isAuthenticated) {
    if (isLoading) {
      return <LoadingScreen />;
    }
    return <LoginScreen onLogin={handleLogin} />;
  }

  // If guest, show guest flight screen
  if (isGuest) {
    return <GuestFlightsScreen onBack={handleLogout} />;
  }

  // Regular authenticated user - show normal flow
  return <Stack screenOptions={{ headerShown: false }} />;
}