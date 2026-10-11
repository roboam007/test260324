from OpenSSL import crypto
import os

# 创建存储证书的目录
cert_dir = os.path.join(os.path.dirname(__file__), 'certs')
os.makedirs(cert_dir, exist_ok=True)

# 生成私钥
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)

# 生成证书
cert = crypto.X509()
cert.get_subject().CN = "localhost"
cert.get_subject().O = "Mock Server"
cert.get_subject().OU = "Development"
cert.set_serial_number(1000)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # 1年有效期
cert.set_issuer(cert.get_subject())
cert.set_pubkey(key)
cert.sign(key, 'sha256')

# 保存证书和私钥
cert_path = os.path.join(cert_dir, 'cert.pem')
key_path = os.path.join(cert_dir, 'key.pem')

with open(cert_path, 'wt') as f:
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode())

with open(key_path, 'wt') as f:
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode())

print(f"✅ 自签名证书生成成功！")
print(f"   证书：{cert_path}")
print(f"   私钥：{key_path}")
