import React, { useEffect, useState } from "react";
import { Alert, PermissionsAndroid, View } from "react-native";
import LoginScreen from "./login";
import LoadingScreen from "./loading";
import GuestFlightsScreen from "./guest-flight";
import HomeScreen from "./home";

export default function RootLayout() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [userData, setUserData] = useState<{
    ticketNumber: string;
    flightNumber: string;
  } | null>(null);

  const requestPermissions = async () => {
    try {
      const result = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS
      );
      if (result === PermissionsAndroid.RESULTS.GRANTED) {
        await requestToken();
      } else {
        Alert.alert(
          "Permission Denied",
          "Notification permissions were denied."
        );
      }
    } catch (error) {
      console.log("Permission request failed:", error);
    }
  };

  const requestToken = async () => {
    try {
      await messaging().registerDeviceForRemoteMessages();
      const token = await messaging().getToken();
      console.log("FCM Token:", token);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    requestPermissions();
  }, []);

  const handleLogin = (ticketNumber: string, flightNumber: string) => {
    setIsLoading(true);

    const guestLogin = ticketNumber === "" && flightNumber === "";

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

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  if (isGuest) {
    return <GuestFlightsScreen onBack={handleLogout} />;
  }

  return <HomeScreen userData={userData} onLogout={handleLogout} />;
}
