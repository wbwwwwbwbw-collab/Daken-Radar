"""
داكن رادار - البلياردو الذكي
الإصدار النهائي 4.0
مع فيزياء كاملة: خطوط الكيوبي + مسار الهدف + نقطة التصادم
"""

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
import math
import time

# جعل الخلفية شفافة تماماً
Window.clearcolor = (0, 0, 0, 0)


class DakenRadar(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # ========== المتغيرات الأساسية ==========
        self.points = []              # [الكرة البيضاء, الكرة الهدف]
        self.ball_radius = Window.width * 0.045  # حجم الكرة تلقائي
        self.tracking = False         # هل نحن في وضع تتبع الكيوبي؟
        self.cue_start = None         # بداية سحب الكيوبي
        self.cue_end = None           # نهاية سحب الكيوبي
        self.tap_times = []           # للنقرات السريعة
        self.long_press_event = None  # حدث الضغطة المطولة
        self.show_physics = True      # إظهار/إخفاء الخطوط الفيزيائية
        
        # ========== إنشاء واجهة المستخدم ==========
        self.create_ui()
        
        # ========== تحديث مستمر ==========
        Clock.schedule_interval(self.update_display, 1/60)
        
        print("=" * 50)
        print("✅ داكن رادار جاهز - النسخة الفيزيائية الكاملة")
        print(f"📏 حجم الكرة: {int(self.ball_radius)} بكسل")
        print("🎯 انقر على الكرة البيضاء ثم على الهدف")
        print("🔴 اضغط مطولاً على الكيوبي لتفعيل التتبع")
        print("=" * 50)
    
    def create_ui(self):
        """إنشاء أزرار التحكم"""
        
        # زر مسح (Reset)
        self.reset_btn = Button(
            text='🗑️ مسح الكل',
            size_hint=(0.14, 0.06),
            pos_hint={'x': 0.84, 'y': 0.92},
            background_color=(0.8, 0.2, 0.2, 0.75),
            color=(1, 1, 1, 1),
            font_size='13sp'
        )
        self.reset_btn.bind(on_press=self.reset_all)
        self.add_widget(self.reset_btn)
        
        # زر إظهار/إخفاء المسارات
        self.toggle_btn = Button(
            text='📏 إخفاء المسارات',
            size_hint=(0.18, 0.06),
            pos_hint={'x': 0.64, 'y': 0.92},
            background_color=(0.3, 0.3, 0.3, 0.75),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        self.toggle_btn.bind(on_press=self.toggle_physics_lines)
        self.add_widget(self.toggle_btn)
        
        # شريط الحالة (أسفل الشاشة)
        self.status_label = Label(
            text='🎯 المرحلة 1: انقر على الكرة البيضاء',
            font_size='15sp',
            size_hint=(0.9, 0.06),
            pos_hint={'x': 0.05, 'y': 0.01},
            color=(1, 1, 0.9, 0.95),
            halign='center',
            valign='middle'
        )
        self.add_widget(self.status_label)
        
        # عداد النقاط
        self.counter_label = Label(
            text='📍 0/2',
            font_size='14sp',
            size_hint=(0.1, 0.05),
            pos_hint={'x': 0.01, 'y': 0.94},
            color=(0.5, 0.8, 1, 0.9),
            halign='left'
        )
        self.add_widget(self.counter_label)
    
    # ========== معالجة اللمس ==========
    
    def on_touch_down(self, touch):
        """معالجة الضغط على الشاشة"""
        
        # تجاهل اللمس فوق الأزرار
        if self.reset_btn.collide_point(*touch.pos) or self.toggle_btn.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        
        # كشف 3 نقرات سريعة (مسح سريع)
        current_time = time.time()
        self.tap_times.append(current_time)
        self.tap_times = [t for t in self.tap_times if current_time - t < 0.4]
        
        if len(self.tap_times) >= 3:
            self.reset_all(None)
            self.tap_times = []
            return True
        
        # ===== المرحلة 1: تحديد النقاط (نقرتان فقط) =====
        if len(self.points) < 2:
            self.points.append((touch.x, touch.y))
            self.draw_balls()
            self.update_status()
            
            if len(self.points) == 1:
                self.status_label.text = '🎯 المرحلة 2: انقر على الكرة الهدف'
                self.counter_label.text = '📍 1/2'
            elif len(self.points) == 2:
                self.status_label.text = '✅ تم التحديد | اضغط مطولاً على الكيوبي لتفعيل التتبع'
                self.counter_label.text = '📍 2/2'
            return True
        
        # ===== المرحلة 2: الضغطة المطولة على الكيوبي =====
        self.long_press_event = Clock.schedule_once(
            lambda dt: self.activate_cue_tracking(touch), 0.5
        )
        return True
    
    def on_touch_move(self, touch):
        """معالجة حركة الإصبع (سحب الكيوبي)"""
        if self.tracking and self.cue_start:
            self.cue_end = (touch.x, touch.y)
    
    def on_touch_up(self, touch):
        """معالجة رفع الإصبع"""
        if self.long_press_event:
            Clock.unschedule(self.long_press_event)
            self.long_press_event = None
        
        if self.tracking:
            self.tracking = False
            self.status_label.text = '🎯 جاهز | اضغط مطولاً على الكيوبي للتوجيه مجدداً'
    
    def activate_cue_tracking(self, touch):
        """تفعيل تتبع الكيوبي مع وميض أحمر"""
        self.tracking = True
        self.cue_start = (touch.x, touch.y)
        self.status_label.text = '🔴 تتبع الكيوبي مفعل | اسحب إصبعك على الكيوبي'
        self.show_red_flash()
    
    def show_red_flash(self):
        """شريط أحمر وامض في منتصف الشاشة للتأكيد"""
        with self.canvas.after:
            Color(1, 0, 0, 0.8)
            flash = Rectangle(pos=(0, Window.height/2 - 8), size=(Window.width, 16))
        Clock.schedule_once(lambda dt: self.canvas.after.remove(flash), 0.3)
    
    # ========== رسم العناصر ==========
    
    def draw_balls(self):
        """رسم الكرات المحددة (لون أزرق شفاف)"""
        self.canvas.before.clear()
        with self.canvas.before:
            for i, p in enumerate(self.points):
                Color(0.2, 0.5, 1, 0.35)  # أزرق شفاف
                Ellipse(
                    pos=(p[0] - self.ball_radius, p[1] - self.ball_radius),
                    size=(self.ball_radius * 2, self.ball_radius * 2)
                )
                # علامة النقطة
                Color(1, 1, 1, 0.7)
                # يمكن إضافة رقم الكرة هنا
    
    def calculate_physics(self):
        """
        حساب الفيزياء الكاملة:
        1. زاوية الكيوبي (مع العكس الفيزيائي)
        2. مسار الكرة البيضاء
        3. مسار الكرة الهدف بعد التصادم
        4. نقطة التصادم بين الكرتين
        """
        if not self.show_physics:
            return None, None, None, None
        
        if not self.tracking or not self.cue_end or len(self.points) < 2:
            return None, None, None, None
        
        cue_ball = self.points[0]      # الكرة البيضاء
        target_ball = self.points[1]   # الكرة الهدف
        
        # ===== 1. حساب زاوية سحبة الإصبع (مع العكس) =====
        dx = self.cue_end[0] - self.cue_start[0]
        dy = self.cue_end[1] - self.cue_start[1]
        
        if dx == 0 and dy == 0:
            return None, None, None, None
        
        # عكس الزاوية فيزيائياً (كلما رفعنا للأعلى تصير الأسفل)
        cue_angle = math.atan2(dy, dx) + math.pi
        
        # ===== 2. خط الكيوبي (مسار البيضاء قبل الاصطدام) =====
        cue_line = (
            cue_ball[0], cue_ball[1],
            cue_ball[0] + math.cos(cue_angle) * 1200,
            cue_ball[1] + math.sin(cue_angle) * 1200
        )
        
        # ===== 3. حساب التصادم بين الكرتين =====
        dx_target = target_ball[0] - cue_ball[0]
        dy_target = target_ball[1] - cue_ball[1]
        distance = math.hypot(dx_target, dy_target)
        
        # نقطة التصادم (عندما تلامس الكرة البيضاء الهدف)
        collision_point = None
        target_line = None
        white_after_line = None
        
        if distance < self.ball_radius * 2.2:  # الكرتان متقاربتان
            # زاوية الخط الواصل بين المراكز
            collision_angle = math.atan2(dy_target, dx_target)
            
            # نقطة التماس بين الكرتين
            contact_x = cue_ball[0] + math.cos(collision_angle) * self.ball_radius * 1.8
            contact_y = cue_ball[1] + math.sin(collision_angle) * self.ball_radius * 1.8
            collision_point = (contact_x, contact_y)
            
            # ===== 4. مسار الكرة الهدف بعد الاصطدام (الخط الرصاصي) =====
            # تتحرك الهدف في نفس اتجاه خط المراكز
            target_line = (
                target_ball[0], target_ball[1],
                target_ball[0] + math.cos(collision_angle) * 700,
                target_ball[1] + math.sin(collision_angle) * 700
            )
            
            # ===== 5. مسار الكرة البيضاء بعد الاصطدام (زاوية 90 درجة) =====
            white_after_angle = collision_angle + math.pi / 2  # زاوية المماس
            white_after_line = (
                cue_ball[0], cue_ball[1],
                cue_ball[0] + math.cos(white_after_angle) * 600,
                cue_ball[1] + math.sin(white_after_angle) * 600
            )
        
        return cue_line, target_line, white_after_line, collision_point
    
    def draw_physics_lines(self):
        """رسم جميع الخطوط الفيزيائية"""
        cue_line, target_line, white_after_line, collision_point = self.calculate_physics()
        
        with self.canvas.after:
            # ===== الخط 1: مسار الكيوبي (أحمر) =====
            if cue_line:
                Color(1, 0.2, 0.2, 0.55)  # أحمر شفاف
                Line(points=cue_line, width=2.5)
            
            # ===== الخط 2: مسار الهدف بعد التصادم (رمادي رصاصي - متقطع) =====
            if target_line:
                Color(0.7, 0.7, 0.7, 0.65)  # رمادي رصاصي
                Line(points=target_line, width=2, dash_length=8, dash_offset=4)
            
            # ===== الخط 3: مسار البيضاء بعد التصادم (أزرق فاتح - متقطع) =====
            if white_after_line:
                Color(0.3, 0.6, 1, 0.5)  # أزرق فاتح
                Line(points=white_after_line, width=1.8, dash_length=6, dash_offset=3)
            
            # ===== نقطة التصادم المتوقعة (دائرة صفراء) =====
            if collision_point:
                Color(1, 0.9, 0, 0.7)  # أصفر ذهبي
                Ellipse(
                    pos=(collision_point[0] - 6, collision_point[1] - 6),
                    size=(12, 12)
                )
    
    def update_display(self, dt):
        """تحديث الشاشة بشكل مستمر"""
        self.canvas.after.clear()
        self.draw_physics_lines()
    
    def update_status(self):
        """تحديث نص الحالة"""
        if len(self.points) == 1:
            self.status_label.text = '🎯 المرحلة 2: انقر على الكرة الهدف'
            self.counter_label.text = '📍 1/2'
        elif len(self.points) == 2:
            self.status_label.text = '✅ تم التحديد | اضغط مطولاً على الكيوبي'
            self.counter_label.text = '📍 2/2'
    
    def toggle_physics_lines(self, instance):
        """إظهار أو إخفاء الخطوط الفيزيائية"""
        self.show_physics = not self.show_physics
        if self.show_physics:
            self.toggle_btn.text = '📏 إخفاء المسارات'
            self.status_label.text = '📏 المسارات ظاهرة'
        else:
            self.toggle_btn.text = '📏 إظهار المسارات'
            self.status_label.text = '📏 المسارات مخفية'
        Clock.schedule_once(lambda dt: self.update_status() if len(self.points) < 2 else None, 1.5)
    
    def reset_all(self, instance):
        """إعادة تعيين كل شيء"""
        self.points = []
        self.tracking = False
        self.cue_start = None
        self.cue_end = None
        self.show_physics = True
        self.toggle_btn.text = '📏 إخفاء المسارات'
        self.canvas.before.clear()
        self.canvas.after.clear()
        self.status_label.text = '🎯 المرحلة 1: انقر على الكرة البيضاء'
        self.counter_label.text = '📍 0/2'
        print("🔄 تم مسح جميع النقاط والمسارات")


# ========== تشغيل التطبيق ==========

class DakenRadarApp(App):
    def build(self):
        return DakenRadar()
    
    def on_start(self):
        print("🚀 تم تشغيل داكن رادار - النسخة الفيزيائية")


if __name__ == '__main__':
    DakenRadarApp().run()