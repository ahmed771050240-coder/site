import 'dart:async';

import 'package:app_links/app_links.dart';
import 'package:flet/flet.dart';
import 'package:material_ui/material_ui.dart';
import 'package:reown_appkit/reown_appkit.dart';

class SultanWalletReownControl extends StatefulWidget {
  final Control control;

  const SultanWalletReownControl({
    super.key,
    required this.control,
  });

  @override
  State<SultanWalletReownControl> createState() =>
      _SultanWalletReownControlState();
}

class _SultanWalletReownControlState extends State<SultanWalletReownControl> {
  ReownAppKitModal? _modal;
  final AppLinks _appLinks = AppLinks();
  StreamSubscription<Uri>? _linkSubscription;
  bool _loading = true;
  String? _error;
  String _address = '';
  String _walletName = '';
  String _chainId = '';

  String get _projectId =>
      widget.control.getString('project_id') ??
      'd49f5ad010ca1d1451ec6eff23e61e0e';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _initialize());
  }

  Future<void> _initialize() async {
    if (!mounted || _modal != null) return;
    try {
      final modal = ReownAppKitModal(
        context: context,
        projectId: _projectId,
        metadata: const PairingMetadata(
          name: 'SULTAN WALLET',
          description: 'Connect your self-custody wallet securely',
          url: 'https://github.com/ahmed771050240-coder/site',
          icons: [
            'https://raw.githubusercontent.com/ahmed771050240-coder/site/main/assets/sultan_wallet_promo.webp',
          ],
          redirect: Redirect(native: 'sultanwallet://'),
        ),
      );

      modal.onModalConnect.subscribe(_onConnect);
      modal.onModalUpdate.subscribe(_onUpdate);
      modal.onModalDisconnect.subscribe(_onDisconnect);
      modal.onModalError.subscribe(_onError);

      await modal.init();
      if (!mounted) return;
      _modal = modal;

      // WalletConnect returns to this app through the registered Android
      // sultanwallet:// scheme. AppLinks forwards the envelope to AppKit.
      final initialLink = await _appLinks.getInitialLink();
      if (initialLink != null) {
        await modal.dispatchEnvelope(initialLink.toString());
      }
      _linkSubscription = _appLinks.uriLinkStream.listen(
        (uri) async {
          try {
            await _modal?.dispatchEnvelope(uri.toString());
          } catch (e) {
            _emitError('تعذر معالجة رابط العودة من المحفظة');
          }
        },
        onError: (_) => _emitError('تعذر استقبال رابط المحفظة'),
      );

      _syncSession();
      setState(() {
        _loading = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'تعذر تهيئة ربط المحافظ. تحقق من اتصال الإنترنت وإعداد Reown.';
      });
      _emitError('AppKit initialization failed');
    }
  }

  void _onConnect(dynamic _) {
    _syncSession();
    if (mounted) setState(() {});
  }

  void _onUpdate(dynamic _) {
    _syncSession();
    if (mounted) setState(() {});
  }

  void _onDisconnect(dynamic _) {
    _address = '';
    _walletName = '';
    _chainId = '';
    widget.control.triggerEvent('wallet_disconnected', <String, dynamic>{});
    if (mounted) setState(() {});
  }

  void _onError(dynamic event) {
    _emitError('حدث خطأ أثناء الاتصال بالمحفظة');
  }

  void _syncSession() {
    final session = _modal?.session;
    if (session == null) return;
    try {
      _address = session.getAddress('eip155') ?? '';
      _walletName = session.connectedWalletName ?? 'محفظة متصلة';
      _chainId = _modal?.selectedChain?.chainId ?? '';
      if (_address.isNotEmpty) {
        widget.control.triggerEvent('wallet_connected', {
          'address': _address,
          'wallet_name': _walletName,
          'chain_id': _chainId,
        });
      }
    } catch (_) {
      // Do not expose SDK internals or sensitive material to the Python app.
    }
  }

  void _emitError(String message) {
    widget.control.triggerEvent('wallet_error', {'message': message});
  }

  @override
  void dispose() {
    _linkSubscription?.cancel();
    final modal = _modal;
    if (modal != null) {
      modal.onModalConnect.unsubscribe(_onConnect);
      modal.onModalUpdate.unsubscribe(_onUpdate);
      modal.onModalDisconnect.unsubscribe(_onDisconnect);
      modal.onModalError.unsubscribe(_onError);
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final modal = _modal;
    final connected = modal?.isConnected ?? false;

    final content = Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF111B32),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0x33D4AF37)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            'ربط المحافظ الرقمية',
            textAlign: TextAlign.right,
            style: TextStyle(
              color: Color(0xFFD4AF37),
              fontSize: 15,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (_loading)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(10),
                child: CircularProgressIndicator(),
              ),
            )
          else if (_error != null)
            Text(
              _error!,
              textAlign: TextAlign.right,
              style: const TextStyle(color: Colors.orangeAccent, fontSize: 12),
            )
          else if (modal == null)
            const Text(
              'خدمة الربط غير جاهزة',
              textAlign: TextAlign.right,
              style: TextStyle(color: Colors.white70),
            )
          else if (connected)
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                AppKitModalAccountButton(appKitModal: modal),
                const SizedBox(height: 8),
                Text(
                  'متصل: $_walletName',
                  textAlign: TextAlign.right,
                  style: const TextStyle(color: Colors.white),
                ),
                Text(
                  _address,
                  textAlign: TextAlign.left,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 11,
                    fontFamily: 'monospace',
                  ),
                ),
                Text(
                  _chainId,
                  textAlign: TextAlign.right,
                  style: const TextStyle(color: Colors.white54, fontSize: 11),
                ),
              ],
            )
          else
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'اتصل عبر WalletConnect. وافق على الاتصال من داخل محفظتك فقط.',
                  textAlign: TextAlign.right,
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                ),
                const SizedBox(height: 10),
                AppKitModalConnectButton(
                  appKit: modal,
                  size: BaseButtonSize.regular,
                ),
              ],
            ),
          const SizedBox(height: 6),
          const Text(
            'لا نطلب عبارة الاسترداد أو المفتاح الخاص. ربط المحفظة لا يعني تفعيل الإيداع أو التحويل المصرفي.',
            textAlign: TextAlign.right,
            style: TextStyle(color: Colors.white38, fontSize: 10),
          ),
        ],
      ),
    );

    return LayoutControl(
      control: widget.control,
      child: ReownAppKitModalTheme(
        isDarkMode: true,
        child: Material(
          color: Colors.transparent,
          child: content,
        ),
      ),
    );
  }
}
