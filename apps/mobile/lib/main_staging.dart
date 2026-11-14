import 'package:flutter/material.dart';
import 'package:secondbrain/core/environment/env.dart';
import 'package:secondbrain/main.dart' as app;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Environment.load();
  runApp(const app.MyApp());
}
