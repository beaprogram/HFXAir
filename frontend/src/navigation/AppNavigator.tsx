import React, { useState } from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { RootStackParamList } from './types';

// Screens
import LoginScreen from '../screens/auth/LoginScreen';
import LoadingScreen from '../screens/auth/LoadingScreen';
import GuestFlightScreen from '../screens/auth/GuestFlightScreen';
import HomeScreen from '../screens/HomeScreen';

const Stack = createStackNavigator<RootStackParamList>();

export default function AppNavigator() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [userData, setUserData] = useState<{ticketNumber: string, flightNumber: string} | null>(null);

  const handleLogin = (ticketNumber: string, flightNumber: string, _response?: any) => {
    setIsLoading(true);
    
    const guestLogin = ticketNumber === '' && flightNumber === '';
    
    setTimeout(() => {
      setIsLoading(false);
      setIsAuthenticated(true);
      setIsGuest(guestLogin);
      
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

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {isLoading ? (
        <Stack.Screen name="Loading" component={LoadingScreen} />
      ) : !isAuthenticated ? (
        <Stack.Screen name="Login">
          {(props) => <LoginScreen {...props} onLogin={handleLogin} />}
        </Stack.Screen>
      ) : isGuest ? (
        <Stack.Screen name="GuestFlight">
          {(props) => <GuestFlightScreen {...props} onBack={handleLogout} />}
        </Stack.Screen>
      ) : (
        <Stack.Screen name="Home">
          {(props) => (
            <HomeScreen 
              {...props} 
              userData={userData} 
              onLogout={handleLogout} 
            />
          )}
        </Stack.Screen>
      )}
    </Stack.Navigator>
  );
}
