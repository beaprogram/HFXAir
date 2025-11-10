import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import FontAwesome from "react-native-vector-icons/FontAwesome";

interface Notification {
  id: string;
  flightNumber: string;
  type: "gate_change" | "status_update" | "delay" | "boarding";
  message: string;
  timestamp: Date;
  read: boolean;
}

interface PushNotificationBannerProps {
  notification: Notification;
  onDismiss: () => void;
}

export const PushNotificationBanner = ({
  notification,
  onDismiss,
}: PushNotificationBannerProps) => {
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "gate_change":
        return "exchange";
      case "status_update":
        return "info-circle";
      case "delay":
        return "clock-o";
      case "boarding":
        return "plane";
      default:
        return "bell";
    }
  };

  return (
    <View style={styles.pushNotificationBanner}>
      <View style={styles.pushNotificationContent}>
        <View style={styles.pushNotificationIcon}>
          <FontAwesome
            name={getNotificationIcon(notification.type)}
            size={20}
            color="#fff"
          />
        </View>
        <View style={styles.pushNotificationText}>
          <Text style={styles.pushNotificationTitle}>
            Flight {notification.flightNumber}
          </Text>
          <Text style={styles.pushNotificationMessage}>
            {notification.message}
          </Text>
        </View>
        <TouchableOpacity
          onPress={onDismiss}
          style={styles.pushNotificationClose}
        >
          <FontAwesome name="times" size={18} color="#fff" />
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  pushNotificationBanner: {
    position: "absolute",
    top: 10,
    left: 16,
    right: 16,
    zIndex: 9999,
    backgroundColor: "#0C2340",
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 100,
  },
  pushNotificationContent: {
    flexDirection: "row",
    padding: 16,
    alignItems: "center",
    gap: 12,
  },
  pushNotificationIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#FFD100",
    justifyContent: "center",
    alignItems: "center",
  },
  pushNotificationText: {
    flex: 1,
  },
  pushNotificationTitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#FFD100",
    marginBottom: 4,
  },
  pushNotificationMessage: {
    fontSize: 13,
    color: "#fff",
    lineHeight: 18,
  },
  pushNotificationClose: {
    padding: 4,
  },
});