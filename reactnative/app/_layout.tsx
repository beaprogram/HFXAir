import React, { useState } from 'react';
import { Stack } from 'expo-router';
import LoginScreen from './login';
import LoadingScreen from './loading';
import GuestFlightsScreen from './guest-flight';

export default function RootLayout() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [userData, setUserData] = useState<{ticketNumber: string, flightNumber: string} | null>(null);

  const handleLogin = (ticketNumber: string, flightNumber: string) => {
    setIsLoading(true);
    
    // Check if it's a guest login (both are empty strings)
    const guestLogin = ticketNumber === '' && flightNumber === '';
    
    setTimeout(() => {
      setIsLoading(false);
      setIsAuthenticated(true);
      setIsGuest(guestLogin);
      
      // Store user data for regular users
      if (!guestLogin) {
        setUserData({ ticketNumber, flightNumber });
      }
    }, 2000);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setIsGuest(false);
    setUserData(null);
  };

  // Show loading screen during authentication
  if (isLoading) {
    return <LoadingScreen />;
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  // If guest, show guest flight screen
  if (isGuest) {
    return (
      <>
        <Stack.Screen name="guest-flight" options={{ headerShown: false }} />
        <GuestFlightsScreen onBack={handleLogout} />
      </>
    );
  }

  // Regular authenticated user - show normal app flow with all screens
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="home" options={{ headerShown: false }} />
      <Stack.Screen name="arrivals" options={{ headerShown: false }} />
      <Stack.Screen name="departures" options={{ headerShown: false }} />
      <Stack.Screen name="airport-map" options={{ headerShown: false }} />
      <Stack.Screen name="shops" options={{ headerShown: false }} />
      <Stack.Screen name="parking" options={{ headerShown: false }} />
      <Stack.Screen name="about" options={{ headerShown: false }} />
    </Stack>
  );
}