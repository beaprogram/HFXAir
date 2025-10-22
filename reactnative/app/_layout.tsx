import React, { useState } from 'react';
import { Stack } from 'expo-router';
import LoginScreen from './login';
import LoadingScreen from './loading';

export default function RootLayout() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  if (!isAuthenticated) {
    if (isLoading) {
      return <LoadingScreen />;
    }
    return <LoginScreen onLogin={() => {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        setIsAuthenticated(true);
      }, 2000);
    }} />;
  }

  return <Stack screenOptions={{ headerShown: false }} />;
}