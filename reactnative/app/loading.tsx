import React from 'react';
import { ActivityIndicator, Text, View } from 'react-native';

export default function LoadingScreen() {
  return (
    <View style={{ 
      flex: 1, 
      justifyContent: 'center', 
      alignItems: 'center', 
      backgroundColor: '#fff' 
    }}>
      <ActivityIndicator size="large" color="#007AFF" />
      <Text style={{ 
        marginTop: 20, 
        fontSize: 18, 
        color: '#333' 
      }}>
        Loading...
      </Text>
    </View>
  );
}
