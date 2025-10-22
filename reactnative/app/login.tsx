import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';

interface LoginScreenProps {
  onLogin: () => void;
}

export default function LoginScreen({ onLogin }: LoginScreenProps) {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' }}>
      <Text style={{ fontSize: 24, marginBottom: 30 }}>Login Page</Text>
      
      <TouchableOpacity
        style={{
          backgroundColor: '#007AFF',
          paddingHorizontal: 30,
          paddingVertical: 15,
          borderRadius: 8,
        }}
        onPress={onLogin}
      >
        <Text style={{ color: 'white', fontSize: 16, fontWeight: 'bold' }}>
          Login
        </Text>
      </TouchableOpacity>
    </View>
  );
}
