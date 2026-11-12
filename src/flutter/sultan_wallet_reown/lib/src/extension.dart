import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';

import 'sultan_wallet_reown.dart';

class Extension extends FletExtension {
  @override
  Widget? createWidget(Key? key, Control control) {
    switch (control.type) {
      case "sultan_wallet_reown":
        return SultanWalletReownControl(key: key, control: control);
      default:
        return null;
    }
  }
}
