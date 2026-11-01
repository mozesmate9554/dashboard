package hu.simcontrol.studio

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat

class MainActivity : FlutterActivity() {
    private var studioFullscreen = false

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "hu.simcontrol.studio/fullscreen")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "setFullscreen" -> {
                        studioFullscreen = call.argument<Boolean>("enabled") == true
                        applyStudioFullscreen()
                        result.success(null)
                    }
                    "getState" -> {
                        val insets = androidx.core.view.ViewCompat.getRootWindowInsets(window.decorView)
                        result.success(mapOf(
                            "requested" to studioFullscreen,
                            "sdk" to android.os.Build.VERSION.SDK_INT,
                            "statusBarVisible" to insets?.isVisible(WindowInsetsCompat.Type.statusBars()),
                            "navigationBarVisible" to insets?.isVisible(WindowInsetsCompat.Type.navigationBars())
                        ))
                    }
                    else -> result.notImplemented()
                }
            }
    }

    private fun applyStudioFullscreen() {
        WindowCompat.setDecorFitsSystemWindows(window, false)
        val controller = WindowCompat.getInsetsController(window, window.decorView)
        controller.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        if (studioFullscreen) controller.hide(WindowInsetsCompat.Type.systemBars())
        else controller.show(WindowInsetsCompat.Type.systemBars())
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus && studioFullscreen) applyStudioFullscreen()
    }
}
