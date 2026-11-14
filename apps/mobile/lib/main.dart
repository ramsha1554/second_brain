import 'package:flutter/material.dart';
import 'package:secondbrain/core/environment/env.dart';

/// Root widget for the Second Brain application.
class MyApp extends StatelessWidget {
  /// Creates the root application widget.
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: Environment.appName,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const MyHomePage(title: 'Second Brain'),
    );
  }
}

/// Home page displaying application environment information.
class MyHomePage extends StatelessWidget {
  /// Creates the home page widget.
  const MyHomePage({required this.title, super.key});

  /// The application title to display.
  final String title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('App ID: ${Environment.appId}'),
            const SizedBox(height: 16),
            Text('API Base URL: ${Environment.apiBaseUrl}'),
          ],
        ),
      ),
    );
  }
}
