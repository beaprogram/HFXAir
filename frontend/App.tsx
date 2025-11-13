import React from 'react';
import { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import AppNavigator from './src/navigation/AppNavigator';
import { PermissionsAndroid } from 'react-native';
import messaging from '@react-native-firebase/messaging';

export default function App() {

  const requestPermisssion = async () =>{
    try{
      const result = await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS)
      if(result === PermissionsAndroid.RESULTS.GRANTED){
        requestToken()
      } else {
        console.log("Permission Denied")
      }
    } catch(error) {
      console.log(error)
    }
  }

  const requestToken = async () =>{
    try{
      await messaging().registerDeviceForRemoteMessages();
      const token = await messaging().getToken();
      console.log("token ==>", token);
    } catch(error){
      console.log(error)
    }
  }

  useEffect(()=>{
    requestPermisssion()
  },[])


  return (
    <NavigationContainer>
      <AppNavigator />
    </NavigationContainer>
  );
}