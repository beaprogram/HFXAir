import React from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import FontAwesome from "react-native-vector-icons/FontAwesome";

interface FlightHeaderProps {
  title: string;
  unreadCount: number;
  isManualRefreshing: boolean;
  onNotificationPress: () => void;
  onRefreshPress: () => void;
}

export const FlightHeader = ({
  title,
  unreadCount,
  isManualRefreshing,
  onNotificationPress,
  onRefreshPress,
}: FlightHeaderProps) => {
  return (
    <View style={styles.embeddedHeader}>
      <Text style={styles.subtitle}>{title}</Text>
      <View style={styles.headerButtons}>
        <TouchableOpacity
          onPress={onNotificationPress}
          style={styles.notificationButtonEmbedded}
          accessibilityRole="button"
          accessibilityLabel={`Notifications${
            unreadCount > 0 ? `, ${unreadCount} unread` : ""
          }`}
          accessibilityHint="Opens notification center"
        >
          <FontAwesome name="bell" size={18} color="#0C2340" />
          {unreadCount > 0 && (
            <View style={styles.notificationBadge}>
              <Text
                style={styles.notificationBadgeText}
                accessibilityElementsHidden={true}
              >
                {unreadCount}
              </Text>
            </View>
          )}
        </TouchableOpacity>
        <TouchableOpacity
          onPress={onRefreshPress}
          disabled={isManualRefreshing}
          style={[styles.refreshButtonEmbedded, styles.headerButton]}
          accessibilityRole="button"
          accessibilityLabel={isManualRefreshing ? "Refreshing" : "Refresh"}
          accessibilityHint="Refreshes the flight information"
          accessibilityState={{ busy: isManualRefreshing }}
        >
          {isManualRefreshing ? (
            <ActivityIndicator size="small" color="#0C2340" />
          ) : (
            <FontAwesome name="refresh" size={18} color="#0C2340" />
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  embeddedHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  subtitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#0C2340",
  },
  headerButtons: {
    flexDirection: "row",
    alignItems: "center",
  },
  headerButton: {
    marginLeft: 8,
  },
  notificationButtonEmbedded: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#fff",
    justifyContent: "center",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 } as const,
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    position: "relative",
  },
  refreshButtonEmbedded: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#fff",
    justifyContent: "center",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 } as const,
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  notificationBadge: {
    position: "absolute",
    top: -2,
    right: -2,
    backgroundColor: "#FF6B6B",
    borderRadius: 10,
    minWidth: 18,
    height: 18,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 2,
    borderColor: "#fff",
  },
  notificationBadgeText: {
    color: "#fff",
    fontSize: 10,
    fontWeight: "bold",
  },
});