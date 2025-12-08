# Luồng Hoạt Động Chức Năng Tích Điểm

Tài liệu này mô tả chi tiết các bước vận hành của hệ thống tích điểm trong module `taphoa_management`, giúp bạn dễ dàng vẽ lại sơ đồ hoặc trao đổi với đội ngũ liên quan.

## 1. Tác nhân & Đối tượng liên quan

| Vai trò/Model | Vai trò chính |
| --- | --- |
| **Khách hàng (res.partner)** | Nhân vật sử dụng điểm, sở hữu thẻ |
| **Thu ngân/POS** | Khởi tạo đơn, áp dụng giảm giá từ điểm |
| **Chương trình (customer.loyalty.program)** | Lưu tỷ lệ tích/đổi, giới hạn giảm giá, hạn dùng |
| **Thẻ (customer.loyalty.card)** | Theo dõi tổng điểm từng khách |
| **Giao dịch (customer.loyalty.transaction)** | Log tích, đổi, điều chỉnh, hết hạn |
| **Cron hết hạn** | Tự động trừ điểm khi đến hạn |

## 2. Chuẩn bị chương trình & thẻ

```mermaid
flowchart TD
    A[Manager cấu hình chương trình\n(customer.loyalty.program)] --> B{Program active?}
    B -- No --> A
    B -- Yes --> C[Thu ngân tạo thẻ \nhoặc gọi partner.create_loyalty_card]
    C --> D[Lưu số thẻ LCxxxxx\n+ gắn chương trình]
    D --> E[Thẻ ở trạng thái active\n sẵn sàng dùng tại POS]
```

> Ghi nhớ: nếu khách chưa có thẻ, hàm `customer.loyalty.card.add_transaction` hoặc `pos.order.create` sẽ tự tạo thẻ mới từ chương trình active đầu tiên.

## 3. Luồng tại quầy POS

```mermaid
sequenceDiagram
    participant KH as Khách hàng
    participant POS as POS UI
    participant Order as pos.order
    participant Card as customer.loyalty.card
    participant Tx as customer.loyalty.transaction

    KH->>POS: Cung cấp thông tin (chọn khách)
    POS->>Card: Truy vấn thẻ active
    alt Không có thẻ
        POS->>Card: Tạo thẻ mới từ program mặc định
    end
    POS->>KH: Hiển thị điểm hiện có
    KH->>POS: Chọn số điểm dùng (tùy chọn)
    POS->>Order: Ghi `loyalty_points_used`
    POS->>Order: Tính `loyalty_discount_amount` qua `program.calculate_discount_from_points`
    POS->>KH: Hiển thị số tiền sau giảm
    KH->>POS: Thanh toán
    POS->>Order: Chuyển trạng thái Paid
    Order->>Tx: (Nếu dùng điểm) tạo giao dịch `redeem`
    Order->>Tx: (Nếu đủ điều kiện) tạo giao dịch `earn`
    Tx->>Card: Cập nhật `total_points`
    Card->>KH: Điểm mới sau giao dịch
```

### Bước chi tiết

1. **Chọn khách hàng:** POS lấy `loyalty_card_id` active; nếu thiếu thì tạo tự động (sử dụng chương trình có `active=True`).
2. **Đổi điểm (tùy chọn):** trường `loyalty_points_used` được validate:
   - Không vượt `card.total_points`.
   - Không nhỏ hơn `program.min_points_to_redeem`.
   - Số tiền giảm giới hạn bởi `program.max_discount_percentage`.
3. **Thanh toán:** `pos.order.action_pos_order_paid()` gọi `_process_loyalty_points()`:
   - Tạo transaction `redeem` (âm điểm) nếu khách dùng điểm.
   - Tạo transaction `earn` với điểm tính từ `program.calculate_points_from_amount()` trên số tiền sau giảm.
4. **Cập nhật:** `customer.loyalty.card._compute_points()` làm mới tổng điểm, đồng thời `res.partner.loyalty_points` phản ánh ra POS.

## 4. Luồng hậu xử lý & đồng bộ

```mermaid
flowchart LR
    PaidOrder[Đơn POS đã Paid] --> EarnTx[Transaction earn confirmed]
    PaidOrder -->|Có discount product| RedeemTx[Transaction redeem confirmed]
    EarnTx --> CardPoints[card.total_points cập nhật]
    RedeemTx --> CardPoints
    CardPoints --> PartnerSync[partner.loyalty_points ghi nhận]
    PartnerSync --> Reports[Báo cáo & Dashboards]
```

- `pos.order.loyalty_transaction_id` trỏ tới giao dịch earn cuối.
- In hóa đơn: `_prepare_invoice_vals` thêm diễn giải giảm giá từ điểm.
- Dashboard/Reports đọc từ các transaction và cards để tổng hợp.

## 5. Hết hạn & Điều chỉnh điểm

```mermaid
flowchart TD
    Cron[Hàng ngày: _cron_expire_points] --> Scan[Quét transaction earn đã quá hạn]
    Scan --> CreateExpire[Tạo transaction type "expire" (âm điểm)]
    CreateExpire --> MarkOld[Đánh dấu transaction gốc = expired]
    MarkOld --> CardUpdate[Card cập nhật total_points]
```

- Manager có thể tạo transaction `adjust` thủ công (tặng/trừ điểm) ở trạng thái nháp rồi **Confirm**.
- Hủy giao dịch chỉ thực hiện khi vẫn là `draft`.

## 6. Lưu đồ tổng quan (từ góc nhìn kinh doanh)

```mermaid
flowchart TD
    subgraph Thiết lập
        P1[Cấu hình chương trình]
        P2[Tạo/Gán thẻ cho khách]
    end
    subgraph Bán hàng POS
        S1[Tạo đơn & chọn khách]
        S2[Tùy chọn đổi điểm]
        S3[Thanh toán]
    end
    subgraph Hậu xử lý
        H1[Tạo giao dịch earn/redeem]
        H2[Cập nhật điểm thẻ]
        H3[Cron hết hạn & báo cáo]
    end

    P1 --> P2 --> S1 --> S2 --> S3 --> H1 --> H2 --> H3
```

## 7. Mốc kiểm soát chính

- **Điểm vào**: `loyalty_points_used` (POS UI) và `order.amount_total`.
- **Điểm ra**: `customer.loyalty.transaction` (log) và `card.total_points`.
- **Rules**: lấy trực tiếp từ `customer.loyalty.program` (tỷ lệ tích, tỷ lệ quy đổi, hạn mức giảm, hạn dùng).
- **Automation**: `_cron_expire_points` bảo vệ việc tồn dư điểm quá hạn.

> Bạn có thể dùng các sơ đồ Mermaid trên trong bất kỳ trình hỗ trợ Mermaid (VS Code, Notion, GitBook...) để render thành flowchart hoặc sequence diagram.
