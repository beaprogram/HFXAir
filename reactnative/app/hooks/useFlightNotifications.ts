import { useState, useEffect } from 'react';
import { Alert } from 'react-native';

export interface Notification {
  id: string;
  flightNumber: string;
  type: 'gate_change' | 'status_update' | 'delay' | 'boarding';
  message: string;
  timestamp: Date;
  read: boolean;
}

interface Flight {
  id: string;
  flightNumber: string;
  notificationsEnabled: boolean;
  [key: string]: any;
}

export const useFlightNotifications = (flights: Flight[], setFlights: (update: (prev: Flight[]) => Flight[]) => void, flightType: 'arrival' | 'departure') => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [currentNotification, setCurrentNotification] = useState<Notification | null>(null);
  const [showNotificationCenter, setShowNotificationCenter] = useState(false);
  const [notificationSequence, setNotificationSequence] = useState<{ [key: string]: number }>({});

  useEffect(() => {
    const simulationInterval = setInterval(() => {
      const enabledFlights = flights.filter(f => f.notificationsEnabled);
      
      if (enabledFlights.length > 0) {
        const randomFlight = enabledFlights[Math.floor(Math.random() * enabledFlights.length)];
        const currentSequence = notificationSequence[randomFlight.id] || 0;
        
        let newNotification: Notification | null = null;
        
        if (currentSequence === 0) {
          const delayMinutes = [15, 30, 45][Math.floor(Math.random() * 3)];
          const [scheduledHours, scheduledMinutes] = randomFlight.scheduledTime.split(':').map(Number);
          const delayedTime = new Date();
          delayedTime.setHours(scheduledHours);
          delayedTime.setMinutes(scheduledMinutes + delayMinutes);
          
          const hours = String(delayedTime.getHours()).padStart(2, '0');
          const minutes = String(delayedTime.getMinutes()).padStart(2, '0');
          const newActualTime = ${hours}:${minutes};
          
          setFlights(prevFlights =>
            prevFlights.map(f =>
              f.id === randomFlight.id ? { ...f, actualTime: newActualTime, status: 'Delayed' as const } : f
            )
          );
          newNotification = {
            id: Date.now().toString(),
            flightNumber: randomFlight.flightNumber,
            type: 'delay',
            message: Flight delayed by ${delayMinutes} minutes. New ${flightType === 'arrival' ? 'arrival' : 'departure'} time: ${newActualTime},
            timestamp: new Date(),
            read: false,
          };
          
          setNotificationSequence(prev => ({
            ...prev,
            [randomFlight.id]: 1
          }));
        } else {
          const newGate = ['A10', 'A15', 'B12', 'B20', 'C8', 'C15'][Math.floor(Math.random() * 6)];
          setFlights(prevFlights =>
            prevFlights.map(f =>
              f.id === randomFlight.id ? { ...f, gate: newGate, status: 'Gate Change' as const } : f
            )
          );
          newNotification = {
            id: Date.now().toString(),
            flightNumber: randomFlight.flightNumber,
            type: 'gate_change',
            message: Gate changed to ${newGate}. Please proceed to the new gate.,
            timestamp: new Date(),
            read: false,
          };
          
          setNotificationSequence(prev => ({
            ...prev,
            [randomFlight.id]: 0
          }));
        }
        
        if (newNotification) {
          setNotifications(prev => [newNotification!, ...prev]);
          setCurrentNotification(newNotification);
          
          setTimeout(() => {
            setCurrentNotification(null);
          }, 10000);
        }
      }
    }, 10000);

    return () => clearInterval(simulationInterval);
  }, [flights, notificationSequence, flightType]);

  const toggleNotification = (flightId: string) => {
    const flight = flights.find(f => f.id === flightId);
    
    setFlights(prevFlights =>
      prevFlights.map(f =>
        f.id === flightId
          ? { ...f, notificationsEnabled: !f.notificationsEnabled }
          : f
      )
    );

    if (flight && !flight.notificationsEnabled) {
      Alert.alert(
        '🔔 Notifications Enabled',
        You will now receive real-time updates for flight ${flight.flightNumber},
        [{ text: 'Got it!' }]
      );
    }
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return {
    notifications,
    currentNotification,
    showNotificationCenter,
    setShowNotificationCenter,
    toggleNotification,
    clearAllNotifications,
    unreadCount,
    setCurrentNotification,
  };
};