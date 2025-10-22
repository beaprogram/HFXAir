import React, { useEffect, useState } from 'react';
import { View, Image, StyleSheet, Animated, Easing } from 'react-native';

export default function LoadingScreen() {
  const [progress] = useState(new Animated.Value(0));

  useEffect(() => {
    Animated.timing(progress, {
      toValue: 1,
      duration: 3000,
      easing: Easing.linear,
      useNativeDriver: false,
    }).start();
  }, []);

  const width = progress.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  return (
    <View style={styles.container}>
      <Image
        source={require('../assets/logo.png')} // replace with your actual logo
        style={styles.logo}
        resizeMode="contain"
      />

      <View style={styles.progressContainer}>
        <Animated.View style={[styles.progressBar, { width }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0C2340',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    width: 200,
    height: 200,
  },
  progressContainer: {
    position: 'absolute',
    bottom: 60,
    width: '80%',
    height: 8,
    backgroundColor: '#1E3A8A',
    borderRadius: 5,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#FFD100',
  },
});