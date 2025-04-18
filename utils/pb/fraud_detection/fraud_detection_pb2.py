# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fraud_detection.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import common_pb2 as common__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15\x66raud_detection.proto\x12\x0e\x66rauddetection\x1a\x0c\x63ommon.proto\"\xb5\x08\n\x12\x46raudDetectionData\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x35\n\x04user\x18\x02 \x01(\x0b\x32\'.frauddetection.FraudDetectionData.User\x12?\n\torderData\x18\x03 \x01(\x0b\x32,.frauddetection.FraudDetectionData.OrderData\x12\x41\n\ncreditCard\x18\x04 \x01(\x0b\x32-.frauddetection.FraudDetectionData.CreditCard\x12I\n\x0e\x62illingAddress\x18\x05 \x01(\x0b\x32\x31.frauddetection.FraudDetectionData.BillingAddress\x12?\n\ttelemetry\x18\x06 \x01(\x0b\x32,.frauddetection.FraudDetectionData.Telemetry\x12(\n\x0bvectorClock\x18\x07 \x01(\x0b\x32\x13.common.VectorClock\x1a%\n\x04User\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontact\x18\x02 \x01(\t\x1a\xb2\x01\n\tOrderData\x12J\n\norderItems\x18\x01 \x03(\x0b\x32\x36.frauddetection.FraudDetectionData.OrderData.OrderItem\x12\x14\n\x0c\x64iscountCode\x18\x02 \x01(\t\x12\x16\n\x0eshippingMethod\x18\x03 \x01(\t\x1a+\n\tOrderItem\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x05\x1a\x41\n\nCreditCard\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x16\n\x0e\x65xpirationDate\x18\x02 \x01(\t\x12\x0b\n\x03\x63vv\x18\x03 \x01(\t\x1a[\n\x0e\x42illingAddress\x12\x0e\n\x06street\x18\x01 \x01(\t\x12\x0c\n\x04\x63ity\x18\x02 \x01(\t\x12\r\n\x05state\x18\x03 \x01(\t\x12\x0b\n\x03zip\x18\x04 \x01(\t\x12\x0f\n\x07\x63ountry\x18\x05 \x01(\t\x1a\xa0\x02\n\tTelemetry\x12\x43\n\x06\x64\x65vice\x18\x01 \x01(\x0b\x32\x33.frauddetection.FraudDetectionData.Telemetry.Device\x12\x45\n\x07\x62rowser\x18\x02 \x01(\x0b\x32\x34.frauddetection.FraudDetectionData.Telemetry.Browser\x12\x18\n\x10screenResolution\x18\x03 \x01(\t\x12\x10\n\x08referrer\x18\x04 \x01(\t\x1a(\n\x07\x42rowser\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x1a\x31\n\x06\x44\x65vice\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\n\n\x02os\x18\x03 \x01(\t\"I\n\x1dInitializeRequestDataResponse\x12(\n\x0bvectorClock\x18\x01 \x01(\x0b\x32\x13.common.VectorClock\"W\n\x1aQuickFraudDetectionRequest\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12(\n\x0bvectorClock\x18\x02 \x01(\x0b\x32\x13.common.VectorClock\"m\n\x1bQuickFraudDetectionResponse\x12\x14\n\x0cisFraudulent\x18\x01 \x01(\x08\x12\x0e\n\x06reason\x18\x02 \x01(\t\x12(\n\x0bvectorClock\x18\x03 \x01(\x0b\x32\x13.common.VectorClock\"_\n\"ComprehensiveFraudDetectionRequest\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12(\n\x0bvectorClock\x18\x02 \x01(\x0b\x32\x13.common.VectorClock\"u\n#ComprehensiveFraudDetectionResponse\x12\x14\n\x0cisFraudulent\x18\x01 \x01(\x08\x12\x0e\n\x06reason\x18\x02 \x01(\t\x12(\n\x0bvectorClock\x18\x03 \x01(\x0b\x32\x13.common.VectorClock\"[\n\x1e\x43learFraudDetectionDataRequest\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12(\n\x0bvectorClock\x18\x02 \x01(\x0b\x32\x13.common.VectorClock\"!\n\x1f\x43learFraudDetectionDataResponse2\xe4\x03\n\x15\x46raudDetectionService\x12j\n\x15InitializeRequestData\x12\".frauddetection.FraudDetectionData\x1a-.frauddetection.InitializeRequestDataResponse\x12k\n\x10\x44\x65tectFraudQuick\x12*.frauddetection.QuickFraudDetectionRequest\x1a+.frauddetection.QuickFraudDetectionResponse\x12\x83\x01\n\x18\x44\x65tectFraudComprehensive\x12\x32.frauddetection.ComprehensiveFraudDetectionRequest\x1a\x33.frauddetection.ComprehensiveFraudDetectionResponse\x12l\n\tClearData\x12..frauddetection.ClearFraudDetectionDataRequest\x1a/.frauddetection.ClearFraudDetectionDataResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'fraud_detection_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_FRAUDDETECTIONDATA']._serialized_start=56
  _globals['_FRAUDDETECTIONDATA']._serialized_end=1133
  _globals['_FRAUDDETECTIONDATA_USER']._serialized_start=464
  _globals['_FRAUDDETECTIONDATA_USER']._serialized_end=501
  _globals['_FRAUDDETECTIONDATA_ORDERDATA']._serialized_start=504
  _globals['_FRAUDDETECTIONDATA_ORDERDATA']._serialized_end=682
  _globals['_FRAUDDETECTIONDATA_ORDERDATA_ORDERITEM']._serialized_start=639
  _globals['_FRAUDDETECTIONDATA_ORDERDATA_ORDERITEM']._serialized_end=682
  _globals['_FRAUDDETECTIONDATA_CREDITCARD']._serialized_start=684
  _globals['_FRAUDDETECTIONDATA_CREDITCARD']._serialized_end=749
  _globals['_FRAUDDETECTIONDATA_BILLINGADDRESS']._serialized_start=751
  _globals['_FRAUDDETECTIONDATA_BILLINGADDRESS']._serialized_end=842
  _globals['_FRAUDDETECTIONDATA_TELEMETRY']._serialized_start=845
  _globals['_FRAUDDETECTIONDATA_TELEMETRY']._serialized_end=1133
  _globals['_FRAUDDETECTIONDATA_TELEMETRY_BROWSER']._serialized_start=1042
  _globals['_FRAUDDETECTIONDATA_TELEMETRY_BROWSER']._serialized_end=1082
  _globals['_FRAUDDETECTIONDATA_TELEMETRY_DEVICE']._serialized_start=1084
  _globals['_FRAUDDETECTIONDATA_TELEMETRY_DEVICE']._serialized_end=1133
  _globals['_INITIALIZEREQUESTDATARESPONSE']._serialized_start=1135
  _globals['_INITIALIZEREQUESTDATARESPONSE']._serialized_end=1208
  _globals['_QUICKFRAUDDETECTIONREQUEST']._serialized_start=1210
  _globals['_QUICKFRAUDDETECTIONREQUEST']._serialized_end=1297
  _globals['_QUICKFRAUDDETECTIONRESPONSE']._serialized_start=1299
  _globals['_QUICKFRAUDDETECTIONRESPONSE']._serialized_end=1408
  _globals['_COMPREHENSIVEFRAUDDETECTIONREQUEST']._serialized_start=1410
  _globals['_COMPREHENSIVEFRAUDDETECTIONREQUEST']._serialized_end=1505
  _globals['_COMPREHENSIVEFRAUDDETECTIONRESPONSE']._serialized_start=1507
  _globals['_COMPREHENSIVEFRAUDDETECTIONRESPONSE']._serialized_end=1624
  _globals['_CLEARFRAUDDETECTIONDATAREQUEST']._serialized_start=1626
  _globals['_CLEARFRAUDDETECTIONDATAREQUEST']._serialized_end=1717
  _globals['_CLEARFRAUDDETECTIONDATARESPONSE']._serialized_start=1719
  _globals['_CLEARFRAUDDETECTIONDATARESPONSE']._serialized_end=1752
  _globals['_FRAUDDETECTIONSERVICE']._serialized_start=1755
  _globals['_FRAUDDETECTIONSERVICE']._serialized_end=2239
# @@protoc_insertion_point(module_scope)
