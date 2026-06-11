from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import os, json, hashlib

app = Flask(__name__)

# Güvenlik ayarları
app.secret_key = os.environ.get('SECRET_KEY', 'yildiz-akademi-gizli-anahtar-2025')
ADMIN_USER = os.environ.get('ADMIN_USER', 'yildiz')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'akademi2025')

# Veritabanı
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///akademi.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ── MODELLER ──────────────────────────────────────────────────

class Ogrenci(db.Model):
    __tablename__ = 'ogrenci'
    id          = db.Column(db.Integer, primary_key=True)
    ad          = db.Column(db.String(200), nullable=False)
    prog        = db.Column(db.String(50), default='sinif')
    sinif       = db.Column(db.String(5), default='8')
    cinsiyet    = db.Column(db.String(10), default='kiz')
    okul        = db.Column(db.String(200), default='')
    ucret       = db.Column(db.Float, default=0)
    tarih       = db.Column(db.String(20), default='')
    veli        = db.Column(db.String(200), default='')
    tel         = db.Column(db.String(50), default='')
    not_        = db.Column('not', db.String(500), default='')
    taksitler   = db.Column(db.Text, default='[]')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':       self.id,
            'ad':       self.ad,
            'prog':     self.prog,
            'sinif':    self.sinif,
            'cinsiyet': self.cinsiyet,
            'okul':     self.okul,
            'ucret':    self.ucret,
            'tarih':    self.tarih,
            'veli':     self.veli,
            'tel':      self.tel,
            'not':      self.not_,
            'taksitler': json.loads(self.taksitler or '[]'),
        }

class Ogretmen(db.Model):
    __tablename__ = 'ogretmen'
    id    = db.Column(db.Integer, primary_key=True)
    ad    = db.Column(db.String(200), nullable=False)
    maas  = db.Column(db.Float, default=0)

    def to_dict(self):
        return {'id': self.id, 'ad': self.ad, 'maas': self.maas}

class Ayar(db.Model):
    __tablename__ = 'ayar'
    key   = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, default='')

# ── GİRİŞ KORUMASI ───────────────────────────────────────────

def giris_gerekli(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('giris_yapildi'):
            if request.path.startswith('/api/'):
                return jsonify({'hata': 'Giriş gerekli'}), 401
            return redirect(url_for('giris'))
        return f(*args, **kwargs)
    return decorated

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    hata = ''
    if request.method == 'POST':
        kullanici = request.form.get('kullanici', '')
        sifre = request.form.get('sifre', '')
        if kullanici == ADMIN_USER and sifre == ADMIN_PASS:
            session['giris_yapildi'] = True
            session.permanent = True
            return redirect(url_for('index'))
        else:
            hata = 'Kullanıcı adı veya şifre hatalı.'
    return render_template('giris.html', hata=hata)

@app.route('/cikis')
def cikis():
    session.clear()
    return redirect(url_for('giris'))

# ── API: ÖĞRENCILER ───────────────────────────────────────────

@app.route('/api/ogrenciler', methods=['GET'])
@giris_gerekli
def ogrenci_list():
    return jsonify([o.to_dict() for o in Ogrenci.query.all()])

@app.route('/api/ogrenciler', methods=['POST'])
@giris_gerekli
def ogrenci_ekle():
    d = request.json
    o = Ogrenci(
        ad=d.get('ad',''),
        prog=d.get('prog','sinif'),
        sinif=d.get('sinif','8'),
        cinsiyet=d.get('cinsiyet','kiz'),
        okul=d.get('okul',''),
        ucret=d.get('ucret',0),
        tarih=d.get('tarih',''),
        veli=d.get('veli',''),
        tel=d.get('tel',''),
        not_=d.get('not',''),
        taksitler=json.dumps(d.get('taksitler',[]), ensure_ascii=False),
    )
    db.session.add(o)
    db.session.commit()
    return jsonify(o.to_dict()), 201

@app.route('/api/ogrenciler/<int:oid>', methods=['PUT'])
@giris_gerekli
def ogrenci_guncelle(oid):
    o = Ogrenci.query.get_or_404(oid)
    d = request.json
    for field in ['ad','prog','sinif','cinsiyet','okul','ucret','tarih','veli','tel']:
        if field in d:
            setattr(o, field, d[field])
    if 'not' in d:
        o.not_ = d['not']
    if 'taksitler' in d:
        o.taksitler = json.dumps(d['taksitler'], ensure_ascii=False)
    db.session.commit()
    return jsonify(o.to_dict())

@app.route('/api/ogrenciler/<int:oid>', methods=['DELETE'])
@giris_gerekli
def ogrenci_sil(oid):
    o = Ogrenci.query.get_or_404(oid)
    db.session.delete(o)
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/ogrenciler/toplu', methods=['POST'])
@giris_gerekli
def ogrenci_toplu():
    liste = request.json
    eklenenler = []
    for d in liste:
        o = Ogrenci(
            ad=d.get('ad',''),
            prog=d.get('prog','sinif'),
            sinif=d.get('sinif','8'),
            cinsiyet=d.get('cinsiyet','kiz'),
            okul=d.get('okul',''),
            ucret=d.get('ucret',0),
            tarih=d.get('tarih',''),
            veli=d.get('veli',''),
            tel=d.get('tel',''),
            not_=d.get('not',''),
            taksitler=json.dumps(d.get('taksitler',[]), ensure_ascii=False),
        )
        db.session.add(o)
        eklenenler.append(o)
    db.session.commit()
    return jsonify([o.to_dict() for o in eklenenler]), 201

# ── API: ÖĞRETMENLER ─────────────────────────────────────────

@app.route('/api/ogretmenler', methods=['GET'])
@giris_gerekli
def ogretmen_list():
    return jsonify([o.to_dict() for o in Ogretmen.query.all()])

@app.route('/api/ogretmenler', methods=['POST'])
@giris_gerekli
def ogretmen_ekle():
    d = request.json
    o = Ogretmen(ad=d.get('ad','Yeni Öğretmen'), maas=d.get('maas',0))
    db.session.add(o)
    db.session.commit()
    return jsonify(o.to_dict()), 201

@app.route('/api/ogretmenler/<int:oid>', methods=['PUT'])
@giris_gerekli
def ogretmen_guncelle(oid):
    o = Ogretmen.query.get_or_404(oid)
    d = request.json
    if 'ad' in d:   o.ad   = d['ad']
    if 'maas' in d: o.maas = d['maas']
    db.session.commit()
    return jsonify(o.to_dict())

@app.route('/api/ogretmenler/<int:oid>', methods=['DELETE'])
@giris_gerekli
def ogretmen_sil(oid):
    o = Ogretmen.query.get_or_404(oid)
    db.session.delete(o)
    db.session.commit()
    return jsonify({'ok': True})

# ── API: AYARLAR ─────────────────────────────────────────────

@app.route('/api/ayarlar', methods=['GET'])
@giris_gerekli
def ayar_list():
    return jsonify({a.key: a.value for a in Ayar.query.all()})

@app.route('/api/ayarlar', methods=['POST'])
@giris_gerekli
def ayar_kaydet():
    d = request.json
    for key, value in d.items():
        a = Ayar.query.get(key)
        if a:
            a.value = str(value)
        else:
            db.session.add(Ayar(key=key, value=str(value)))
    db.session.commit()
    return jsonify({'ok': True})

# ── ANASAYFA ─────────────────────────────────────────────────

@app.route('/')
@giris_gerekli
def index():
    return render_template('index.html')

# ── BAŞLAT ───────────────────────────────────────────────────

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
